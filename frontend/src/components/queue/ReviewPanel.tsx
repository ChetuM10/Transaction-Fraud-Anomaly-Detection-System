import { useState } from "react";
import type { Flag } from "../../types/fraud";
import { submitReview } from "../../api/client";
import { ShapChart } from "./ShapChart";
import { X, ShieldCheck, ShieldX } from "lucide-react";

interface ReviewPanelProps {
  flag: Flag;
  onClose: () => void;
  onReviewed: () => void;
}

export function ReviewPanel({ flag, onClose, onReviewed }: ReviewPanelProps) {
  const [submitting, setSubmitting] = useState(false);
  const [reviewerName, setReviewerName] = useState("");

  const handleReview = async (outcome: "true_positive" | "false_positive") => {
    if (!reviewerName.trim()) {
      alert("Please enter your name before submitting.");
      return;
    }

    try {
      setSubmitting(true);
      await submitReview(flag.id, {
        outcome,
        reviewed_by: reviewerName.trim(),
      });
      onReviewed();
    } catch (err: any) {
      alert(err.message || "Failed to submit review.");
    } finally {
      setSubmitting(false);
    }
  };
}
