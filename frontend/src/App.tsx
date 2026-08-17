import { useState } from "react";
import { Sidebar } from "./components/layout/Sidebar";

export default function App() {
  //this remembers which tab is currently active
  const [activeTab, setActiveTab] = useState<"overview" | "queue">("queue");

  return (
    <div className="flex min-h-screen bg-background text-white">
      {/* left sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* main content */}
      <div className="flex-1 p-8 overflow-auto">
        {/* simple paceholder for now */}
        {activeTab === "overview" && (
          <div>
            <h1 className="text-3xl font-bol mb-4"> Overview Dashboard</h1>
            <p className="text-gray-400">KPIs and Charts will go here...</p>
          </div>
        )}

        {activeTab === "queue" && (
          <div>
            <h1 className="text-3xl font-bold mb-4">Reviewer Queue</h1>
            <p className="text-gray-400">Table transactions will go here...</p>
          </div>
        )}
      </div>
    </div>
  );
}
