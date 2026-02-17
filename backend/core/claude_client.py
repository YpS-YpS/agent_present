from __future__ import annotations

import json
from typing import Any, AsyncIterator

import anthropic

from backend.agents.base_agent import BaseAgent


class ClaudeClient:
    """Anthropic SDK client that implements the tool-use agent loop."""

    def __init__(self, api_key: str, model: str, max_tokens: int = 4096):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    async def run_agent_loop(
        self,
        agent: BaseAgent,
        session_id: str,
        messages: list[dict],
        max_iterations: int = 10,
    ) -> AsyncIterator[dict]:
        """Core agent loop with token usage tracking."""
        tools = agent.get_tools()
        system = agent.system_prompt

        total_input_tokens = 0
        total_output_tokens = 0

        for iteration in range(max_iterations):
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=messages,
                tools=tools,
            )

            # Track token usage
            if response.usage:
                total_input_tokens += response.usage.input_tokens
                total_output_tokens += response.usage.output_tokens

            # Collect text and tool_use blocks
            text_parts = []
            tool_use_blocks = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            # Yield any text
            if text_parts:
                full_text = "\n".join(text_parts)
                yield {"type": "text", "content": full_text}

            # If no tool calls, we're done — yield final token usage
            if not tool_use_blocks:
                yield {
                    "type": "token_usage",
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "model": self.model,
                }
                return

            # Execute tool calls and build results
            tool_results = []
            for tool_block in tool_use_blocks:
                yield {"type": "tool_start", "tool_name": tool_block.name}

                result = await agent.execute_tool(
                    tool_block.name, dict(tool_block.input), session_id
                )

                # Check if result is a chart
                if isinstance(result, dict) and result.get("type") == "chart":
                    yield {"type": "chart", "data": result["plotly_json"]}
                    tool_result_content = json.dumps({"type": "chart", "status": "chart_rendered"})
                elif isinstance(result, dict) and result.get("type") == "error":
                    tool_result_content = json.dumps(result)
                else:
                    tool_result_content = json.dumps(result, default=str)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": tool_result_content,
                })

                yield {"type": "tool_end", "tool_name": tool_block.name}

            # Append assistant response and tool results to messages for next iteration
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        # If we hit max iterations, yield usage and warning
        yield {
            "type": "token_usage",
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "model": self.model,
        }
        yield {"type": "text", "content": "\n\n*[Analysis reached maximum iteration limit]*"}
