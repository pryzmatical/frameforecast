import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, XAxis, YAxis } from "recharts";

interface FpsRangeChartProps {
  low: number;
  predicted: number;
  high: number;
}

export function FpsRangeChart({ low, predicted, high }: FpsRangeChartProps) {
  const data = [{ name: "Estimated FPS", base: low, range: Math.max(high - low, 0.1) }];
  const domainMax = Math.max(Math.ceil((high + Math.max(high - low, 5)) / 10) * 10, 10);

  return (
    <div data-testid="fps-range-chart" className="h-28 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical" margin={{ top: 8, right: 24, bottom: 8, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2e3540" horizontal={false} />
          <XAxis
            type="number"
            domain={[0, domainMax]}
            tick={{ fill: "#9ca3af", fontSize: 12 }}
            stroke="#2e3540"
          />
          <YAxis type="category" dataKey="name" hide />
          <Bar dataKey="base" stackId="fps" fill="transparent" isAnimationActive={false} />
          <Bar
            dataKey="range"
            stackId="fps"
            fill="#c084fc"
            radius={[4, 4, 4, 4]}
            isAnimationActive={false}
          />
          <ReferenceLine
            x={predicted}
            stroke="#e6edf3"
            strokeWidth={2}
            label={{ value: `${predicted} FPS`, position: "top", fill: "#e6edf3", fontSize: 13 }}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
