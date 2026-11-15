import { useCallback, useEffect, useState } from "react";
import {
  Users,
  RefreshCw,
  Building2,
  Activity,
  ShieldCheck,
  LoaderCircle,
} from "lucide-react";
import { api } from "../services/api";

export default function AgentDirectory() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAgents = useCallback(async () => {
    setLoading(true);

    try {
      const data = await api.getAgents();
      setAgents(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to load agents.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  const activeAgents = agents.filter((agent) => agent.is_active).length;

  return (
    <div className="workspace-page">
      <div className="section-heading">
        <div>
          <div className="page-eyebrow">NETWORK PARTICIPANTS</div>
          <h2>Agent Directory</h2>
          <p>Enterprise agents registered in the AgentSphere network.</p>
        </div>

        <button
          className="button secondary"
          onClick={loadAgents}
          disabled={loading}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && <div className="feedback-message error">{error}</div>}

      <div className="agent-metrics">
        <div className="panel agent-metric">
          <div className="metric-icon-new purple">
            <Users size={18} />
          </div>
          <span>Total registered agents</span>
          <strong>{agents.length}</strong>
        </div>

        <div className="panel agent-metric">
          <div className="metric-icon-new green">
            <Activity size={18} />
          </div>
          <span>Active agents</span>
          <strong>{activeAgents}</strong>
        </div>

        <div className="panel agent-metric">
          <div className="metric-icon-new blue">
            <Building2 size={18} />
          </div>
          <span>Industries represented</span>
          <strong>
            {new Set(agents.map((agent) => agent.industry_category)).size}
          </strong>
        </div>
      </div>

      <div className="agent-directory-heading">
        <div>
          <h3>Registered enterprises</h3>
          <p>Agent identity, interests and network trust.</p>
        </div>
        <span>{agents.length} agents</span>
      </div>

      {loading && !agents.length ? (
        <div className="panel feed-empty">
          <LoaderCircle size={22} />
          <p>Loading registered agents...</p>
        </div>
      ) : agents.length === 0 ? (
        <div className="panel feed-empty">
          <Users size={25} />
          <h3>No registered agents</h3>
          <p>Registered enterprise agents will appear here.</p>
        </div>
      ) : (
        <div className="agent-grid">
          {agents.map((agent) => (
            <article className="panel agent-card" key={agent.id}>
              <div className="agent-card-header">
                <div className="company-avatar-new agent-avatar">
                  {(agent.company_name || "A").slice(0, 1).toUpperCase()}
                </div>

                <span
                  className={`agent-status ${
                    agent.is_active ? "active" : "inactive"
                  }`}
                >
                  <span />
                  {agent.is_active ? "Active" : "Inactive"}
                </span>
              </div>

              <h3>{agent.company_name}</h3>
              <span className="agent-industry">{agent.industry_category}</span>

              <div className="agent-interest">
                <span>INTEREST MANIFESTO</span>
                <p>{agent.interest_manifesto || "No interests specified."}</p>
              </div>

              <div className="agent-card-footer">
                <div>
                  <ShieldCheck size={15} />
                  <span>Trust score</span>
                </div>
                <strong>
                  {agent.trust_score != null
                    ? Number(agent.trust_score).toFixed(2)
                    : "N/A"}
                </strong>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
