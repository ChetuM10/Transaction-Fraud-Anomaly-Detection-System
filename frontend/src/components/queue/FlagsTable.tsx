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
}
