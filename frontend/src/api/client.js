import axios from "axios";

// In dev, VITE_API_URL is unset and Vite proxies /api → localhost:8000.
// In production (GitHub Pages), VITE_API_URL is set to the Render backend URL.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// --- Users ---
export const createUser = (username) =>
  api.post("/users", { chess_com_username: username }).then((r) => r.data);

// --- Games ---
export const syncGames = (username, months = 3) =>
  api.post("/games/sync", { username, months }).then((r) => r.data);

export const getGames = (username, page = 1, perPage = 20) =>
  api
    .get("/games", { params: { username, page, per_page: perPage } })
    .then((r) => r.data);

// --- Analysis ---
export const getAnalysisStatus = (jobId) =>
  api.get(`/analysis/status/${jobId}`).then((r) => r.data);

// --- Weaknesses ---
export const getWeaknesses = (username) =>
  api.get(`/weaknesses/${username}`).then((r) => r.data);

// --- Resources ---
export const getResources = (category, username) =>
  api.get(`/resources/${category}`, { params: { username } }).then((r) => r.data);

export const completeResource = (resourceId, username) =>
  api
    .patch(`/resources/${resourceId}/complete`, { username })
    .then((r) => r.data);

export default api;
