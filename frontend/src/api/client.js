import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// --- Users ---
export const createUser = (username) =>
  api.post("/users", { chess_com_username: username }).then((r) => r.data);

// --- Games ---
export const syncGames = (username, months = 3, testMode = false) =>
  api.post("/games/sync", { username, months, test_mode: testMode }).then((r) => r.data);

export const runTestAnalysis = (username) =>
  api.post("/analysis/run-test", null, { params: { username } }).then((r) => r.data);

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
