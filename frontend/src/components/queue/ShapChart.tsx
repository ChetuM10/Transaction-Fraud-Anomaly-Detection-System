import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { FeatureExplanation } from "../../types/fraud";

interface ShapChartProps {
  features: FeatureExplanation[];
}

export function ShapChart({ features }: ShapChartProps) {
  // sorts features by abs SHAP value(biggest first)
  const sorted = [...features].sort(
    (a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value),
  );

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sorted} layout="vertical" margin={{ left: 100 }}>
          <XAxis type="number" tick={{ fill: "#9ca3af", fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="feature"
            tick={{ fill: "#d1d5db", fontSize: 12 }}
            width={100}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#18181b",
              border: "1px solid #27272a",
              borderRadius: "8px",
              color: "#fff",
            }}
            formatter={(value: number | string | undefined, _name: string, props: any) => [
              `SHAP: ${typeof value === 'number' ? value.toFixed(4) : value} | Actual: ${props.payload.actual_value}`,
              props.payload.feature,
            ]}
          />
          <Bar
            dataKey="shap_value"
            radius={[0, 4, 4, 0]}
            shape={(props: any) => {
              const fill = props.shap_value >= 0 ? "#ef4444" : "#10b981";
              return <rect {...props} fill={fill} />;
            }}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
