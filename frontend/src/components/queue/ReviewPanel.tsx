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

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-card border border-border rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-xl font-bold text-white">Transaction Review</h2>
            <p className="text-xs text-gray-400 font-mono mt-1">
              {flag.transaction_id}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>
        {/* Info Grid */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-background rounded-lg p-4 border border-border">
            <p className="text-xs text-gray-400 mb-1">Risk Score</p>
            <p
              className={`text-2xl font-bold ${
                flag.score >= 0.7
                  ? "text-rose-400"
                  : flag.score >= 0.4
                    ? "text-amber-400"
                    : "text-emerald-400"
              }`}
            >
              {(flag.score * 100).toFixed(1)}%
            </p>
          </div>
          <div className="bg-background rounded-lg p-4 border border-border">
            <p className="text-xs text-gray-400 mb-1">Decision</p>
            <p className="text-lg font-semibold text-white capitalize">
              {flag.decision.replace("_", " ")}
            </p>
          </div>
          <div className="bg-background rounded-lg p-4 border border-border">
            <p className="text-xs text-gray-400 mb-1">Current Outcome</p>
            <p className="text-lg font-semibold text-white capitalize">
              {flag.outcome.replace("_", " ")}
            </p>
          </div>
        </div>
        {/* SHAP Chart */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3">
            Feature Explanations (SHAP)
          </h3>
          <div className="bg-background rounded-lg p-4 border border-border">
            <ShapChart features={flag.top_features} />
          </div>
        </div>
        {/* Review Actions */}
        {flag.outcome === "pending" && (
          <div className="space-y-4 border-t border-border pt-4">
            <div>
              <label className="text-xs text-gray-400 block mb-1">
                Reviewer Name
              </label>
              <input
                type="text"
                value={reviewerName}
                onChange={(e) => setReviewerName(e.target.value)}
                placeholder="Enter your name"
                className="bg-background border border-border text-sm text-white rounded-md
                  px-3 py-2 w-full focus:outline-none focus:border-gray-500"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => handleReview("true_positive")}
                disabled={submitting}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5
                  bg-rose-950 text-rose-400 border border-rose-800 rounded-lg
                  hover:bg-rose-900 transition-colors disabled:opacity-50 font-medium text-sm"
              >
                <ShieldX className="w-4 h-4" />
                Confirm Fraud
              </button>
              <button
                onClick={() => handleReview("false_positive")}
                disabled={submitting}
                className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5
                  bg-emerald-950 text-emerald-400 border border-emerald-800 rounded-lg
                  hover:bg-emerald-900 transition-colors disabled:opacity-50 font-medium text-sm"
              >
                <ShieldCheck className="w-4 h-4" />
                False Positive
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
