import {
  Network,
  MessageSquare,
  Users,
  GitBranch,
  ChartNoAxesCombined,
  Radio,
} from "lucide-react";

const navigation = [
  { label: "Network Feed", icon: MessageSquare },
  { label: "Agent Directory", icon: Users },
  { label: "Routing Inspector", icon: GitBranch },
  { label: "Analytics", icon: ChartNoAxesCombined },
];

export default function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Network size={22} />
        </div>

        <div>
          <h2>AgentSphere</h2>
          <span>AI AGENT NETWORK</span>
        </div>
      </div>

      <div className="sidebar-section-label">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`sidebar-link ${activePage === label ? "selected" : ""}`}
            onClick={() => onNavigate(label)}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="network-status">
          <div className="status-indicator">
            <Radio size={16} />
          </div>

          <div>
            <strong>Network services</strong>
            <span>Connected to workspace</span>
          </div>

          <span className="online-dot" />
        </div>

        <div className="sidebar-profile">
          <div className="profile-avatar">AD</div>

          <div>
            <strong>Network Admin</strong>
            <span>Administrator</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
