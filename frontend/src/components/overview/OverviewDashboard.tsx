import { useEffect, useState } from "react";
import type { Flag } from "../../types/fraud";
import { fetchFlags } from "../../api/client";
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  XCircle,
  TrendingUp,
} from "lucide-react";
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
}
