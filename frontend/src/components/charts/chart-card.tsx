"use client";

import React, { Component, useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Maximize2, Minimize2, Download, AlertTriangle, Loader2 } from "lucide-react";
import type { PlotlyChartData } from "@/lib/types";

/* Error boundary to catch Plotly render crashes */
interface EBProps {
  children: React.ReactNode;
}
interface EBState {
  error: string | null;
}

class ChartErrorBoundary extends Component<EBProps, EBState> {
  state: EBState = { error: null };

  static getDerivedStateFromError(err: Error) {
    return { error: err.message };
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex h-full flex-col items-center justify-center gap-2 text-xs text-zinc-500">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          <span>Chart render error</span>
          <span className="max-w-md truncate text-zinc-600">{this.state.error}</span>
        </div>
      );
    }
    return this.props.children;
  }
}

interface ChartCardProps {
  chart: PlotlyChartData;
}

/**
 * Renders a Plotly chart using the imperative API (Plotly.react) instead of
 * react-plotly.js. This avoids dynamic import issues with the factory pattern
 * and works reliably with plotly.js-dist-min.
 */
function PlotlyChart({
  data,
  layout,
  config,
  style,
}: {
  data: any[];
  layout: any;
  config: any;
  style?: React.CSSProperties;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      try {
        const Plotly = await import("plotly.js-dist-min");
        const PlotlyLib = Plotly.default || Plotly;

        if (cancelled || !containerRef.current) return;

        await PlotlyLib.react(containerRef.current, data, layout, config);
        if (!cancelled) setLoading(false);
      } catch (err: any) {
        if (!cancelled) {
          setError(err.message || "Failed to render chart");
          setLoading(false);
        }
      }
    }

    render();

    return () => {
      cancelled = true;
      if (containerRef.current) {
        import("plotly.js-dist-min").then((Plotly) => {
          const PlotlyLib = Plotly.default || Plotly;
          if (containerRef.current) {
            PlotlyLib.purge(containerRef.current);
          }
        }).catch(() => {});
      }
    };
  }, [data, layout, config]);

  // Handle resize
  useEffect(() => {
    if (loading || !containerRef.current) return;

    const handleResize = () => {
      import("plotly.js-dist-min").then((Plotly) => {
        const PlotlyLib = Plotly.default || Plotly;
        if (containerRef.current) {
          PlotlyLib.Plots.resize(containerRef.current);
        }
      }).catch(() => {});
    };

    window.addEventListener("resize", handleResize);
    // Trigger initial resize after render
    handleResize();
    return () => window.removeEventListener("resize", handleResize);
  }, [loading]);

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-xs text-zinc-500">
        <AlertTriangle className="h-5 w-5 text-amber-500" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div style={style} className="relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center text-xs text-zinc-500">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Loading chart...
        </div>
      )}
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}

export function ChartCard({ chart }: ChartCardProps) {
  const [expanded, setExpanded] = useState(false);

  const title = chart.layout?.title?.text || chart.layout?.title || "Chart";

  const handleDownload = () => {
    const plotEl = document.querySelector(".js-plotly-plot") as any;
    if (plotEl && (window as any).Plotly) {
      (window as any).Plotly.downloadImage(plotEl, {
        format: "png",
        width: 1200,
        height: 600,
        filename: `presentmon-chart-${Date.now()}`,
      });
    }
  };

  return (
    <Card className="overflow-hidden border-border/50 bg-zinc-950 w-full">
      <div className="flex items-center justify-between border-b border-border/30 px-4 py-2.5">
        <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">
          {typeof title === "string" ? title : "Chart"}
        </span>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-zinc-500 hover:text-zinc-200"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <Minimize2 className="h-3.5 w-3.5" />
            ) : (
              <Maximize2 className="h-3.5 w-3.5" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-zinc-500 hover:text-zinc-200"
            onClick={handleDownload}
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>
      <div className={expanded ? "h-[550px]" : "h-[350px]"}>
        <ChartErrorBoundary>
          <PlotlyChart
            data={chart.data || []}
            layout={{
              ...chart.layout,
              autosize: true,
              margin: { l: 60, r: 30, t: 10, b: 50 },
              title: undefined,
              legend: {
                ...chart.layout?.legend,
                orientation: "h" as const,
                y: -0.15,
                x: 0.5,
                xanchor: "center" as const,
              },
            }}
            config={{
              responsive: true,
              displayModeBar: true,
              displaylogo: false,
              modeBarButtonsToRemove: ["lasso2d", "select2d"],
            }}
            style={{ width: "100%", height: "100%" }}
          />
        </ChartErrorBoundary>
      </div>
    </Card>
  );
}
