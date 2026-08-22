import { useEffect, useState } from "react";
import type { Flag } from "../../types/fraud";
import { fetchFlags } from "../../api/client";
import { ShieldAlert, Clock, XCircle, TrendingUp } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

export function OverviewDashboard() {
  const [flags, setFlags] = useState<Flag[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchFlags();
        setFlags(data);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard metrics.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  //summary stats
  const totalFlags = flags.length;
  const pendingCount = flags.filter((f) => f.outcome === "pending").length;
  const confirmedFraudCount = flags.filter(
    (f) => f.outcome === "true_positive",
  ).length;
  const autoBlockedCount = flags.filter(
    (f) => f.decision === "auto_block",
  ).length;

  const avgRiskScore =
    totalFlags > 0
      ? (
          (flags.reduce((sum, f) => sum + f.score, 0) / totalFlags) *
          100
        ).toFixed(1)
      : "0.0";

  //chart data
  const decisionData = [
    {
      name: "Auto Block",
      count: flags.filter((f) => f.decision === "auto_block").length,
      fill: "#ef4444",
    },
    {
      name: "Needs Review",
      count: flags.filter((f) => f.decision === "review").length,
      fill: "#f59e0b",
    },
    {
      name: "Auto Approve",
      count: flags.filter((f) => f.decision === "auto_approve").length,
      fill: "#10b981",
    },
  ];

  if (loading) {
    return (
      <div className="p-8 text-center text-gray-400">
        Loading overview metrics...
      </div>
    );
  }

  if (error) {
    return <div className="p-8 text-center text-rose-400"></div>;
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">System Overview</h1>
        <p className="text-sm text-gray-400">
          High-level metrics and decision volume acress all processed
          transactions.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Flags */}
        <div className="bg-card border border border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase">Total Flags</span>
            <ShieldAlert className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-white">{totalFlags}</p>
          <p className="text-xs text-gray-500">Processed by ML Pipeline</p>
        </div>

        {/* Pending Reviews */}
        <div className="bg-card border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase">
              Pending Action
            </span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bol text-rose-400">{pendingCount}</p>
          <p className="text-xs text-gray-500">Awaiting human analyst review</p>
        </div>

        {/* Card 3: Confirmed Fraud */}
        <div className="bg-card border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase">
              Confirmed Fraud
            </span>
            <XCircle className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-2xl font-bold text-rose-400">
            {confirmedFraudCount}
          </p>
          <p className="text-xs text-gray-500">Marked True Positive</p>
        </div>

        {/* Avg Risk Score */}
        <div className="bg-card border border-border p-5 rounded-xl space-y-2">
          <div className="flex items-center justify-between text-gray-400">
            <span className="text-xs font-medium uppercase">
              Avg Risk Score
            </span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-white">{avgRiskScore}%</p>
          <p className="text-xs text-gray-500">
            {autoBlockedCount} auto-blocked immediately
          </p>
        </div>
      </div>

      {/* Decision Ditribution Chart */}
      <div className="bg-card border border-border p-6 rounded-xl space-y-4">
        <h2 className="text-base font-semibold text-white">
          Decision Volume Distribution
        </h2>
        <div className="w-full h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={decisionData} margin={{ top: 20, bottom: 20 }}>
              <XAxis
                dataKey="name"
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={{ stroke: "#27272a" }}
              />
              <YAxis
                tick={{ fill: "#9ca3af", fontSize: 12 }}
                axisLine={{ stroke: "#27272a" }}
                allowDecimals={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#18181b",
                  border: "1px solid #27272a",
                  borderRadius: "8px",
                  color: "#fff",
                }}
              />
              <Bar
                dataKey="count"
                radius={[6, 6, 0, 0]}
                shape={(props: any) => {
                  const fill = props.payload.fill || "#6366f1";
                  return <rect {...props} fill={fill} />;
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
