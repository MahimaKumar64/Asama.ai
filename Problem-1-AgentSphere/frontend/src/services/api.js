const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || `API request failed: ${response.status}`);
  }

  return data;
}

export const api = {
  getAgents: () => apiRequest("/agents"),

  getPosts: () => apiRequest("/posts"),

  getRouting: () => apiRequest("/routing"),

  getEngagement: () => apiRequest("/analytics/engagement"),

  registerAgent: (agent) =>
    apiRequest("/agents/register", {
      method: "POST",
      body: JSON.stringify(agent),
    }),

  createPost: (post) =>
    apiRequest("/posts", {
      method: "POST",
      body: JSON.stringify(post),
    }),

  addComment: (postId, comment) =>
    apiRequest(`/posts/${postId}/comments`, {
      method: "POST",
      body: JSON.stringify(comment),
    }),

  processFeedback: () =>
    apiRequest("/analytics/process-feedback", {
      method: "POST",
    }),

  getSimulationStatus: () => apiRequest("/simulation/status"),

  startSimulation: () =>
    apiRequest("/simulation/start", {
      method: "POST",
    }),

  stopSimulation: () =>
    apiRequest("/simulation/stop", {
      method: "POST",
    }),
};
