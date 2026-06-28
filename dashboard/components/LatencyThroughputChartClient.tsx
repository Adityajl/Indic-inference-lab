"use client";

import dynamic from "next/dynamic";

const LatencyThroughputChart = dynamic(() => import("./LatencyThroughputChart"), {
  ssr: false,
  loading: () => <div className="max-w-5xl mx-auto px-6 py-12 h-80" />,
});

export default LatencyThroughputChart;