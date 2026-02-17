declare module "react-plotly.js" {
  import { Component } from "react";

  interface PlotParams {
    data: any[];
    layout?: any;
    frames?: any[];
    config?: any;
    style?: React.CSSProperties;
    className?: string;
    useResizeHandler?: boolean;
    onInitialized?: (figure: any, graphDiv: any) => void;
    onUpdate?: (figure: any, graphDiv: any) => void;
    onPurge?: (figure: any, graphDiv: any) => void;
    onError?: (err: any) => void;
  }

  class Plot extends Component<PlotParams> {}
  export default Plot;
}

declare module "react-plotly.js/factory" {
  import { ComponentType } from "react";
  function createPlotlyComponent(plotly: any): ComponentType<any>;
  export default createPlotlyComponent;
}

declare module "plotly.js-dist-min" {
  const Plotly: any;
  export default Plotly;
}
