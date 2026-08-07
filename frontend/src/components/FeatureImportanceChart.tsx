import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { FeatureImportance } from "../types";

interface FeatureImportanceChartProps {
  data: FeatureImportance[];
}

export function FeatureImportanceChart({ data }: FeatureImportanceChartProps) {
  const top = [...data].sort((a, b) => b.importance - a.importance).slice(0, 8);
  const chartData = top.map((entry) => ({
    label: entry.label,
    percent: Math.round(entry.importance * 1000) / 10,
  }));

  return (
    <div data-testid="feature-importance-chart" className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3540" horizontal={false} />
          <XAxis
            type="number"
            unit="%"
            tick={{ fill: "#9ca3af", fontSize: 12 }}
            stroke="#2e3540"
          />
          <YAxis
            type="category"
            dataKey="label"
            width={150}
            tick={{ fill: "#9ca3af", fontSize: 12 }}
            stroke="#2e3540"
          />
          <Tooltip
            formatter={(value) => [`${value}%`, "Relative importance"]}
            contentStyle={{ background: "#16171d", border: "1px solid #2e3540", color: "#e6edf3" }}
          />
          <Bar dataKey="percent" fill="#c084fc" radius={[0, 4, 4, 0]} isAnimationActive={false} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
