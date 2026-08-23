import { useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";
import { FlagsTable } from "./components/queue/FlagsTable";
import { ReviewPanel } from "./components/queue/ReviewPanel";
import { OverviewDashboard } from "./components/overview/OverviewDashboard";
import type { Flag } from "./types/fraud";

export default function App() {
  //this remembers which tab is currently active
  const [activeTab, setActiveTab] = useState<"overview" | "queue">("queue");
  const [selectedFlag, setSelectedFlag] = useState<Flag | null>(null);

  return (
    <div className="flex min-h-screen bg-background text-white">
      {/* left sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* main content */}
      <div className="flex-1 p-8 overflow-auto">
        {/* simple paceholder for now */}
        {activeTab === "overview" && <OverviewDashboard />}

        {activeTab === "queue" && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold mb-4">Reviewer Queue</h1>
              <p className="text-gray-400">
                Inspect high-risk transactions and submit analyst decisions.
              </p>
            </div>

            {/* table rendering */}
            <FlagsTable onSelectFlag={(flag) => setSelectedFlag(flag)} />
          </div>
        )}
      </div>

      {/* REVIEW - RENDERS WHEN A FLAG IS SELECTED */}
      {selectedFlag && (
        <ReviewPanel
          flag={selectedFlag}
          onClose={() => setSelectedFlag(null)}
          onReviewed={() => {
            setSelectedFlag(null);
          }}
        />
      )}
    </div>
  );
}
