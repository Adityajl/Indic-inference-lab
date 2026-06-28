"use client";

import dynamic from "next/dynamic";

const TokenEfficiencyChart = dynamic(() => import("./TokenEfficiencyChart"), {
  ssr: false,
  loading: () => <div className="max-w-5xl mx-auto px-6 py-12 h-80" />,
});

export default TokenEfficiencyChart;