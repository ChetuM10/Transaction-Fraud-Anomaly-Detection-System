import { LayoutDashboard, ListTodo, ShieldAlert } from "lucide-react";

interface SidebarProps {
  activeTab: "overview" | "queue";
  setActiveTab: (tab: "overview" | "queue") => void;
}

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  return (
    <div className="w-14 md:w-64 h-screen bg-card border-r border-border flex flex-col shrink-0">
      {/* Brand logo */}
      <div className="h-16 flex items-center justify-center md:justify-start px-2 md:px-6 border-b border-border">
        <ShieldAlert className="w-6 h-6 text-brand-red md:mr-3" />
        <span className="hidden md:inline text-white font-bold tracking-wider">LUCID</span>
      </div>

      {/* Navigation links */}
      <div className="flex-1 py-6 px-2 md:px-4 space-y-2">
        {/* Overview Button */}
        <button
          onClick={() => setActiveTab("overview")}
          title="Overview"
          className={`w-full flex items-center justify-center md:justify-start px-2 md:px-4 py-3 rounded-md transition-colors ${
            activeTab === "overview"
              ? "bg-border text-white"
              : "text-gray-400 hover:bg-border/50 hover:text-white"
          }`}
        >
          <LayoutDashboard className="w-5 h-5 md:mr-3" />
          <span className="hidden md:inline">Overview</span>
        </button>

        {/* Queue Button */}
        <button
          onClick={() => setActiveTab("queue")}
          title="Reviewer Queue"
          className={`w-full flex items-center justify-center md:justify-start px-2 md:px-4 py-3 rounded-md transition-colors ${
            activeTab === "queue"
              ? "bg-border text-white"
              : "text-gray-400 hover:bg-border/50 hover:text-white"
          }`}
        >
          <ListTodo className="w-5 h-5 md:mr-3" />
          <span className="hidden md:inline">Reviewer Queue</span>
        </button>
      </div>
    </div>
  );
}
