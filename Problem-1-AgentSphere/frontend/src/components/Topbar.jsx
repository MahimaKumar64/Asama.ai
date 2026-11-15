import { Search, Bell, RefreshCw } from "lucide-react";

export default function Topbar({ activePage, onRefresh }) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <span>Workspace</span>
        <span className="breadcrumb-divider">/</span>
        <strong>{activePage}</strong>
      </div>

      <div className="topbar-actions">
        <div className="search-box">
          <Search size={16} />
          <input placeholder="Search network..." />
          <span>⌘ K</span>
        </div>

        <button
          className="topbar-icon"
          title="Refresh dashboard"
          onClick={onRefresh}
        >
          <RefreshCw size={17} />
        </button>

        <button className="topbar-icon notification-icon">
          <Bell size={18} />
          <span className="notification-dot" />
        </button>

        <div className="topbar-avatar">A</div>
      </div>
    </header>
  );
}
