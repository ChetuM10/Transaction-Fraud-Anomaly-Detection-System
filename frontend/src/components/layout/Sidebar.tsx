import { LayoutDashboard, ListTodo, ShieldAlert } from "lucide-react";

interface SidebarProps {
  activeTab: "overview" | "queue";
  setActiveTab: (tab: "overview" | "queue") => void;
}

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  return (
    <div className="w-64 h-screen bg-card border-r border-border flex flex-col">
      {/* Brand logo */}
      <div className="h-16 flex items-center px-6 border-b border-border">
        <ShieldAlert className="w-6 h-6 text-brand-red mr-3" />
        <span className="text-white font-bold tracking-wider">LUCID</span>
      </div>

      {/* Navigation links */}
      <div className="flex-1 py-6 px-4 space-y-2">
        {/* Overview Button */}
        <button
          onClick={() => setActiveTab("overview")}
          className={`w-full flex items-center px-4 py-3 rounded-md transition-colors ${
            activeTab === "overview"
              ? "bg-border text-white"
              : "text-gray-400 hover:bg-border/50 hover:text-white"
          }`}
        >
          <LayoutDashboard className="w-5 h-5 mr-3" />
          Overview
        </button>

        {/* Queue Button */}
        <button
          onClick={() => setActiveTab("queue")}
          className={`w-full flex items-center px-4 py-3 rounded-md transition-colors ${
            activeTab === "queue"
              ? "bg-border text-white"
              : "text-gray-400 hover:bg-border/50 hover:text-white"
          }`}
        >
          <ListTodo className="w-5 h-5 mr-3" />
          Reviewer Queue
        </button>
      </div>
    </div>
  );
}
