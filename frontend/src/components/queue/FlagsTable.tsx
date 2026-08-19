import { useEffect, useState } from "react";
import type { Flag } from "../../types/fraud";
import { fetchFlags } from "../../api/client";
import {
  AlertCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Eye,
} from "lucide-react";

interface FlagsTableProps {
  onSelectFlag: (flag: Flag) => void;
}

export function FlagsTable({ onSelectFlag }: FlagsTableProps) {
  const [flags, setFlags] = useState<Flag[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [filterDecision, setFilterDecision] = useState<string>("");
  const [filterOutcome, setFilterOutcome] = useState<string>("pending");

  //load flags from backend
  const loadFlags = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchFlags(
        filterDecision || undefined,
        filterOutcome || undefined,
      );
      setFlags(data);
    } catch (err: any) {
      setError(err.message || "Failed to load flags.");
    } finally {
      setLoading(false);
    }
  };

  //   fetch again if filter changes
  useEffect(() => {
    loadFlags();
  }, [filterDecision, filterOutcome]);

  //helper for decision badges
  const renderDecisionBadge = (decision: string) => {
    switch (decision) {
      case "auto_approve":
        return (
          <span
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs
          font-medium bg-emeral-950 text-emerald-400 border border-emerald-800"
          >
            <CheckCircle2 className="w-3 h-3 mr-1" /> Approve
          </span>
        );
      case "auto_block":
        return (
          <span
            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs
          font-medium bg-rose-950 text-rose-400 border border-rose-800"
          >
            <XCircle className="w-3 h-3 mr-1" /> Block
          </span>
        );
      default:
        return (
          <span
            className="inline-flex items-center px-2.5 py-0.5 rounded-fill text-xs
          font-medium bg-amber-950 text-amber-400 border border-amber-800"
          >
            <AlertCircle className="w-3 h-3 mr-1" /> Review
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* header and filter bar */}
      <div
        className="felx flex-col sm:flex-row justify-between items-start sm:items-center
      gap-4 bg-card p-4 rounded-lg border border-border"
      >
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-400">Filters:</span>

          {/* outcome filter */}
          <select
            value={filterOutcome}
            onChange={(e) => setFilterOutcome(e.target.value)}
            className="bg-background border border-border text-xs text-white rounded-md
              px-d3 py-1.5 focus:outline-none focus:border-gray-500"
          >
            <option value="">All Outcomes</option>
            <option value="pending">Pending Review</option>
            <option value="true_positive">Confirmed Fraud</option>
            <option value="flase_positive">False Positive</option>
          </select>

          {/* Decision Filter */}
          <select
            value={filterDecision}
            onChange={(e) => setFilterDecision(e.target.value)}
            className="bg-background border border-border text-xs text-white rounded-md
            px-d3 py-1.5 focus:outline-none focus:border-gray-500"
          >
            <option value="">All Decisions</option>
            <option value="review">Needs Review</option>
            <option value="auto_block">Auto Blocked</option>
            <option value="auto+_approve">Auto Approved</option>
          </select>
        </div>

        <button
          onClick={loadFlags}
          className="inline-flex items-center text-xs text-gray-300 hover:text-white
        bg-background border border-border hover:bg-border/50 px-3 py-1.5 rounded-md transition-colors"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>
    </div>
  );
}
