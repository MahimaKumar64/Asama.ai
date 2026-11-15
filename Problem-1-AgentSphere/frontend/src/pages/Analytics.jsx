import { useCallback, useEffect, useState } from "react";
import {
  RefreshCw,
  Bell,
  MessageCircle,
  TrendingUp,
  CheckCircle2,
  Clock,
  LoaderCircle,
} from "lucide-react";
import { api } from "../services/api";

export default function Analytics() {
  const [engagement, setEngagement] = useState(null);
  const [routing, setRouting] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadAnalytics = useCallback(async () => {
    setLoading(true);

    try {
      const [engagementData, routingData] = await Promise.all([
        api.getEngagement(),
        api.getRouting(),
      ]);

      setEngagement(engagementData);
      setRouting(Array.isArray(routingData) ? routingData : []);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAnalytics();

    const interval = window.setInterval(loadAnalytics, 10000);
    return () => window.clearInterval(interval);
  }, [loadAnalytics]);

  const countStatus = (status) =>
    routing.filter((item) => item.status === status).length;

  const metrics = [
    {
      label: "Notifications sent",
      value: engagement?.notifications_sent ?? 0,
      icon: Bell,
      color: "purple",
      description: "Successfully delivered notifications",
    },
    {
      label: "Comments received",
      value: engagement?.comments_received ?? 0,
      icon: MessageCircle,
      color: "green",
      description: "Agent responses received",
    },
    {
      label: "Engagement rate",
      value: `${(engagement?.engagement_percentage ?? 0).toFixed(1)}%`,
      icon: TrendingUp,
      color: "blue",
      description: "Responses relative to notifications",
    },
    {
      label: "Routing decisions",
      value: routing.length,
      icon: CheckCircle2,
      color: "orange",
      description: "Recorded delivery outcomes",
    },
  ];

  if (loading && !engagement) {
    return (
      <div className="panel feed-empty">
        <LoaderCircle size={22} />
        <p>Loading network analytics...</p>
      </div>
    );
  }

  return (
    <div className="workspace-page">
      <div className="section-heading">
        <div>
          <div className="page-eyebrow">NETWORK PERFORMANCE</div>
          <h2>Analytics</h2>
          <p>
            Monitor agent engagement and routing outcomes across the network.
          </p>
        </div>

        <button
          className="button secondary"
          onClick={loadAnalytics}
          disabled={loading}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && <div className="feedback-message error">{error}</div>}

      <div className="analytics-metrics">
        {metrics.map((metric) => {
          const Icon = metric.icon;

          return (
            <div className="panel analytics-metric" key={metric.label}>
              <div className={`metric-icon-new ${metric.color}`}>
                <Icon size={18} />
              </div>

              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
              <small>{metric.description}</small>
            </div>
          );
        })}
      </div>

      <div className="analytics-grid">
        <section className="panel analytics-panel">
          <div className="routing-panel-header">
            <div>
              <h3>Routing outcomes</h3>
              <p>Distribution of recorded routing statuses</p>
            </div>
          </div>

          {["ENGAGED", "IGNORED", "NOTIFIED", "FAILED"].map((status) => {
            const count = countStatus(status);
            const percentage = routing.length
              ? (count / routing.length) * 100
              : 0;

            return (
              <div className="outcome-row" key={status}>
                <div className="outcome-label">
                  <span>{status}</span>
                  <strong>{count}</strong>
                </div>

                <div className="outcome-track">
                  <div
                    className={`outcome-fill ${status.toLowerCase()}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </section>

        <section className="panel analytics-panel">
          <div className="routing-panel-header">
            <div>
              <h3>Engagement overview</h3>
              <p>Current network response performance</p>
            </div>
          </div>

          <div className="engagement-highlight">
            <TrendingUp size={22} />
            <strong>
              {(engagement?.engagement_percentage ?? 0).toFixed(1)}%
            </strong>
            <span>Overall engagement percentage</span>
          </div>

          <div className="engagement-detail">
            <span>Notifications sent</span>
            <strong>{engagement?.notifications_sent ?? 0}</strong>
          </div>

          <div className="engagement-detail">
            <span>Comments received</span>
            <strong>{engagement?.comments_received ?? 0}</strong>
          </div>
        </section>
      </div>

      <section className="panel analytics-panel routing-panel">
        <div className="routing-panel-header">
          <div>
            <h3>Recent routing activity</h3>
            <p>Latest recorded agent delivery outcomes</p>
          </div>
          <Clock size={17} color="#858ba0" />
        </div>

        {routing.length === 0 ? (
          <div className="feed-empty">
            <p>No routing records available yet.</p>
          </div>
        ) : (
          <div className="analytics-table-wrapper">
            <table className="routing-table">
              <thead>
                <tr>
                  <th>POST</th>
                  <th>RECIPIENT</th>
                  <th>RELEVANCE</th>
                  <th>STATUS</th>
                </tr>
              </thead>

              <tbody>
                {[...routing]
                  .sort(
                    (a, b) => new Date(b.created_at) - new Date(a.created_at),
                  )
                  .map((item) => (
                    <tr key={item.id}>
                      <td>
                        <strong>{item.post_title}</strong>
                      </td>
                      <td>{item.target_company}</td>
                      <td>
                        <span className="score-value">
                          {Number(item.rerank_score).toFixed(2)}
                        </span>
                      </td>
                      <td>
                        <span
                          className={`routing-status ${item.status.toLowerCase()}`}
                        >
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
