"use client";
import { BarChart, Bar, XAxis, YAxis } from "recharts";

export default function DiagnosticTestChart() {
  const data = [
    { name: "A", value: 10 },
    { name: "B", value: 20 },
    { name: "C", value: 15 },
  ];
  return (
    <div style={{ width: 400, height: 300, background: "white" }}>
      <BarChart width={400} height={300} data={data}>
        <XAxis dataKey="name" />
        <YAxis />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
    </div>
  );
}