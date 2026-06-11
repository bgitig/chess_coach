import { useState } from "react";
import { createUser, syncGames } from "../api/client.js";
import AnalysisProgress from "./AnalysisProgress.jsx";

export default function SyncPanel({ username, onUsernameChange }) {
  const [input, setInput] = useState(username);
  const [months, setMonths] = useState(3);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSync = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);
    setMessage(null);
    setJobId(null);

    try {
      await createUser(input.trim());
      onUsernameChange(input.trim().toLowerCase());

      const result = await syncGames(input.trim(), months);
      if (result.job_id) {
        setJobId(result.job_id);
        setMessage(`Synced ${result.games_queued} games. Analysis started.`);
      } else {
        setMessage(result.message);
      }
    } catch (err) {
      const detail = err.response?.data?.detail || err.message;
      setError(`Sync failed: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-8">
      <h2 className="text-lg font-semibold text-white mb-4">Sync Your Games</h2>
      <form onSubmit={handleSync} className="flex flex-wrap gap-3 items-end">
        <div className="flex-1 min-w-48">
          <label className="block text-sm text-gray-400 mb-1">Chess.com Username</label>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="e.g. hikaru"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Months</label>
          <select
            value={months}
            onChange={(e) => setMonths(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
          >
            <option value={1}>1 month</option>
            <option value={2}>2 months</option>
            <option value={3}>3 months</option>
            <option value={6}>6 months</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-6 py-2 rounded-lg transition-colors"
        >
          {loading ? "Syncing..." : "Sync Games"}
        </button>
      </form>

      {message && <p className="text-green-400 text-sm mt-3">{message}</p>}
      {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

      <AnalysisProgress
        jobId={jobId}
        onComplete={() => setMessage("Analysis complete! Refresh the dashboard.")}
      />
    </div>
  );
}
