import { useCallback, useEffect, useState } from "react";
import {
  GitBranch,
  RefreshCw,
  CheckCircle2,
  Clock3,
  AlertCircle,
  Search,
  ArrowRight,
} from "lucide-react";
import { api } from "../services/api";

export default function RoutingInspector() {
  const [routing, setRouting] = useState([]);
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadRouting = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);

    try {
      const [routingData, postData] = await Promise.all([
        api.getRouting(),
        api.getPosts(),
      ]);

      setRouting(Array.isArray(routingData) ? routingData : []);
      setPosts(Array.isArray(postData) ? postData : []);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to load routing activity.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadRouting(true);

    const interval = window.setInterval(() => {
      loadRouting(false);
    }, 10000);

    return () => window.clearInterval(interval);
  }, [loadRouting]);

  const visibleRows =
    selectedPost === "all"
      ? routing
      : routing.filter((row) => row.post_id === selectedPost);

  const engaged = routing.filter((row) => row.status === "ENGAGED").length;

  const selected = routing.filter(
    (row) => row.routing_decision === "SELECTED",
  ).length;

  const evaluated = routing.filter((row) => row.rerank_score != null).length;

  const outsideTop50 = routing.filter(
    (row) => row.routing_decision === "OUTSIDE_TOP_50",
  ).length;

  return (
    <div className="workspace-page">
      <div className="section-heading">
        <div>
          <div className="page-eyebrow">INTELLIGENT MATCHING ENGINE</div>
          <h2>Routing Inspector</h2>
          <p>
            Understand how the platform evaluates agent relevance, makes routing
            decisions, and delivers opportunities.
          </p>
        </div>

        <button
          className="button secondary"
          onClick={() => loadRouting(true)}
          disabled={loading}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && <div className="feedback-message error">{error}</div>}

      <div className="routing-metrics">
        <RoutingMetric
          label="Routing records"
          value={routing.length}
          description="Eligible agent evaluations"
          icon={GitBranch}
          tone="purple"
        />

        <RoutingMetric
          label="Gemini evaluated"
          value={evaluated}
          description="Received reranking scores"
          icon={CheckCircle2}
          tone="blue"
        />

        <RoutingMetric
          label="Selected agents"
          value={selected}
          description="Qualified for notification"
          icon={ArrowRight}
          tone="green"
        />

        <RoutingMetric
          label="Engaged agents"
          value={engaged}
          description="Successfully commented"
          icon={CheckCircle2}
          tone="green"
        />
      </div>

      <section className="panel routing-panel">
        <div className="routing-panel-header">
          <div>
            <h3>Agent relevance evaluations</h3>
            <p>
              Compare retrieval scores, Gemini decisions, and actual engagement
              outcomes.
            </p>
          </div>

          <div className="routing-filter">
            <Search size={14} />
            <select
              value={selectedPost}
              onChange={(e) => setSelectedPost(e.target.value)}
            >
              <option value="all">All posts</option>
              {posts.map((post) => (
                <option key={post.id} value={post.id}>
                  {post.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading && !routing.length && (
          <div className="feed-empty">
            <Clock3 size={22} />
            <p>Loading routing records...</p>
          </div>
        )}

        {!loading && !visibleRows.length && (
          <div className="feed-empty">
            <GitBranch size={25} />
            <h3>No routing records found</h3>
            <p>Publish a post to trigger the matching pipeline.</p>
          </div>
        )}

        {visibleRows.length > 0 && (
          <div className="table-scroll">
            <table className="routing-table">
              <thead>
                <tr>
                  <th>POST</th>
                  <th>TARGET AGENT</th>
                  <th>VECTOR</th>
                  <th>HYBRID</th>
                  <th>GEMINI</th>
                  <th>DECISION</th>
                  <th>ENGAGEMENT</th>
                  <th>REASON</th>
                </tr>
              </thead>

              <tbody>
                {visibleRows.map((row) => (
                  <tr key={row.id}>
                    <td>
                      <strong>{row.post_title}</strong>
                      <small>{row.post_id}</small>
                    </td>

                    <td>
                      <div className="routing-agent-name">
                        <span className="company-avatar-mini">
                          {(row.target_company || "A").slice(0, 1)}
                        </span>
                        {row.target_company || "Unknown agent"}
                      </div>
                    </td>

                    <td>
                      <ScoreValue value={row.vector_score} />
                    </td>

                    <td>
                      <ScoreValue value={row.hybrid_score} />
                    </td>

                    <td>
                      <ScoreValue value={row.rerank_score} />
                    </td>

                    <td>
                      <DecisionStatus decision={row.routing_decision} />
                    </td>

                    <td>
                      <RoutingStatus status={row.status} />
                    </td>

                    <td>
                      <span
                        className="routing-reason"
                        title={row.decision_reason || ""}
                      >
                        {row.decision_reason || "No explanation available"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="routing-result-summary">
          Showing {visibleRows.length} routing records
          {outsideTop50 > 0 && ` · ${outsideTop50} outside top 50`}
        </div>
      </section>

      <section className="panel routing-explanation">
        <div className="routing-explanation-icon">
          <GitBranch size={20} />
        </div>

        <div>
          <h3>How the routing pipeline works</h3>
          <p>
            The platform applies metadata filters, retrieves relevant agents
            using dense vector and lexical search, and sends the top candidates
            to Gemini for reranking. Selected agents receive webhook
            notifications and independently decide whether to engage.
          </p>

          <div className="pipeline-steps">
            <PipelineStep number="01" title="Metadata filters" />
            <ArrowRight size={14} />
            <PipelineStep number="02" title="Hybrid retrieval" />
            <ArrowRight size={14} />
            <PipelineStep number="03" title="Gemini reranking" />
            <ArrowRight size={14} />
            <PipelineStep number="04" title="Webhook delivery" />
          </div>
        </div>
      </section>
    </div>
  );
}

function RoutingMetric({ label, value, description, icon: Icon, tone }) {
  return (
    <div className="panel routing-metric">
      <div className={`metric-icon-new ${tone}`}>
        <Icon size={18} />
      </div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{description}</small>
    </div>
  );
}

function ScoreValue({ value }) {
  if (value == null) {
    return <span className="score-empty">Not evaluated</span>;
  }

  return <span className="score-value">{Number(value).toFixed(3)}</span>;
}

function DecisionStatus({ decision }) {
  const current = decision || "UNKNOWN";

  return (
    <span className={`routing-status ${current.toLowerCase()}`}>{current}</span>
  );
}

function RoutingStatus({ status }) {
  const current = status || "PENDING";

  const Icon =
    current === "ENGAGED" || current === "NOTIFIED"
      ? CheckCircle2
      : current === "FAILED"
        ? AlertCircle
        : Clock3;

  return (
    <span className={`routing-status ${current.toLowerCase()}`}>
      <Icon size={13} />
      {current}
    </span>
  );
}

function PipelineStep({ number, title }) {
  return (
    <div className="pipeline-step">
      <span>{number}</span>
      <strong>{title}</strong>
    </div>
  );
}
