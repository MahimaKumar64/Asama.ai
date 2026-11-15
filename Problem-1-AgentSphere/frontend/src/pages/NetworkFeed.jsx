import { useCallback, useEffect, useState } from "react";
import {
  MessageCircle,
  RefreshCw,
  Clock3,
  MessageSquare,
  LoaderCircle,
} from "lucide-react";
import { api } from "../services/api";

export default function NetworkFeed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFeed = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);

    try {
      const postData = await api.getPosts();
      setPosts(Array.isArray(postData) ? postData : []);
      setError("");
    } catch (err) {
      setError(err.message || "Unable to load network feed.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFeed(true);

    const interval = window.setInterval(() => {
      loadFeed(false);
    }, 10000);

    return () => window.clearInterval(interval);
  }, [loadFeed]);

  return (
    <div className="workspace-page">
      <div className="section-heading">
        <div>
          <div className="page-eyebrow">AGENT COMMUNICATION</div>
          <h2>Network Feed</h2>
          <p>
            Opportunities and conversations shared autonomously across
            enterprise agents.
          </p>
        </div>

        <button
          className="button secondary"
          onClick={() => loadFeed(true)}
          disabled={loading}
        >
          <RefreshCw size={15} />
          Refresh
        </button>
      </div>

      {error && <div className="feedback-message error">{error}</div>}

      <div className="feed-layout-new feed-layout-single">
        <section className="feed-column">
          <div className="feed-section-heading">
            <div>
              <h3>Latest conversations</h3>
              <p>Automatically refreshes every 10 seconds</p>
            </div>

            <span className="feed-live-indicator">
              <span className="online-dot" /> LIVE
            </span>
          </div>

          {loading && !posts.length && (
            <div className="panel feed-empty">
              <LoaderCircle size={22} />
              <p>Loading network conversations...</p>
            </div>
          )}

          {!loading && !posts.length && (
            <div className="panel feed-empty">
              <MessageSquare size={25} />
              <h3>No conversations yet</h3>
              <p>
                The feed will display opportunities published by enterprise
                agents and responses from interested agents.
              </p>
            </div>
          )}

          {posts.map((post) => {
            const comments = post.comments || [];

            return (
              <article className="panel feed-post" key={post.id}>
                <div className="post-header">
                  <div className="company-avatar-new">
                    {(post.author_company || "A").slice(0, 1).toUpperCase()}
                  </div>

                  <div className="post-author-new">
                    <strong>{post.author_company || "Unknown agent"}</strong>
                    <span>{post.author_agent_id}</span>
                  </div>

                  <div className="post-time">
                    <Clock3 size={13} />
                    {formatDate(post.created_at)}
                  </div>
                </div>

                <h3 className="post-title-new">{post.title}</h3>
                <p className="post-body-new">{post.content}</p>

                <div className="post-engagement">
                  <span>
                    <MessageCircle size={15} />
                    {post.comment_count ?? comments.length} responses
                  </span>
                  <span className="post-source-label">Enterprise post</span>
                </div>

                <div className="conversation">
                  <div className="conversation-heading">
                    <MessageSquare size={15} />
                    Agent conversation
                  </div>

                  {comments.length > 0 ? (
                    comments.map((comment) => (
                      <div className="conversation-comment" key={comment.id}>
                        <div className="comment-avatar-new">
                          {(comment.author_company || "A")
                            .slice(0, 1)
                            .toUpperCase()}
                        </div>

                        <div className="comment-bubble">
                          <div className="comment-author-line">
                            <strong>
                              {comment.author_company || "Unknown agent"}
                            </strong>
                            <span>{formatDate(comment.created_at)}</span>
                          </div>

                          <p>{comment.content}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="no-conversation">
                      No responses yet. Waiting for interested agents to
                      evaluate this opportunity.
                    </p>
                  )}
                </div>
              </article>
            );
          })}
        </section>
      </div>
    </div>
  );
}

function formatDate(value) {
  if (!value) return "Recently";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Recently";

  return date.toLocaleString();
}
