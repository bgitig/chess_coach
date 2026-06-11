import { useEffect, useRef, useState } from "react";
import { getGames } from "../api/client.js";

const STATUS_STYLES = {
  done: "bg-green-900 text-green-300",
  running: "bg-blue-900 text-blue-300 animate-pulse",
  pending: "bg-gray-700 text-gray-300",
  failed: "bg-red-900 text-red-300",
};

const STATUS_LABELS = {
  done: "done",
  running: "analyzing",
  pending: "pending",
  failed: "failed",
};

const RESULT_STYLES = {
  win: "text-green-400",
  loss: "text-red-400",
  draw: "text-yellow-400",
};

function formatDate(dateStr) {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function GameLibrary({ username }) {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const pollRef = useRef(null);

  const fetchGames = (showSpinner = false) => {
    if (!username) return;
    if (showSpinner) setLoading(true);
    setError(null);
    getGames(username, page)
      .then((d) => {
        setData(d);
        const hasActive = d.games.some(
          (g) => g.analysis_status === "running" || g.analysis_status === "pending"
        );
        clearInterval(pollRef.current);
        if (hasActive) {
          pollRef.current = setInterval(() => fetchGames(false), 3000);
        }
      })
      .catch((err) => {
        const detail = err.response?.data?.detail || err.message;
        setError(detail);
      })
      .finally(() => { if (showSpinner) setLoading(false); });
  };

  useEffect(() => {
    fetchGames(true);
    return () => clearInterval(pollRef.current);
  }, [username, page]);

  if (!username) {
    return (
      <div className="text-center py-20 text-gray-500">
        <p>Enter your username to view your game library.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-20 text-gray-400">
        <p>Loading games...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20 text-red-400">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!data || !data.games.length) {
    return (
      <div className="text-center py-20 text-gray-500">
        <p>No games found. Sync your games first.</p>
      </div>
    );
  }

  const totalPages = Math.ceil(data.total / data.per_page);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">
          Game Library
          <span className="text-gray-400 font-normal text-lg ml-2">— {username}</span>
        </h2>
        <span className="text-gray-400 text-sm">{data.total} total games</span>
      </div>

      {/* Table */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-800 text-gray-400 uppercase text-xs">
              <tr>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Opening</th>
                <th className="px-4 py-3 text-left">Color</th>
                <th className="px-4 py-3 text-left">Result</th>
                <th className="px-4 py-3 text-left">Opp. Rating</th>
                <th className="px-4 py-3 text-left">Time Control</th>
                <th className="px-4 py-3 text-left">Analysis</th>
                <th className="px-4 py-3 text-left">Blunders</th>
                <th className="px-4 py-3 text-left">Mistakes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {data.games.map((g) => (
                <tr key={g.id} className="hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3 text-gray-300 whitespace-nowrap">
                    {formatDate(g.played_at)}
                  </td>
                  <td className="px-4 py-3 text-gray-400">{g.eco_code || "—"}</td>
                  <td className="px-4 py-3 text-gray-300 capitalize">{g.color_played || "—"}</td>
                  <td className={`px-4 py-3 font-medium capitalize ${RESULT_STYLES[g.result] || "text-gray-400"}`}>
                    {g.result || "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-300">{g.opponent_rating ?? "—"}</td>
                  <td className="px-4 py-3 text-gray-400">{g.time_control || "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[g.analysis_status] || "bg-gray-700 text-gray-300"}`}>
                      {STATUS_LABELS[g.analysis_status] ?? g.analysis_status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {g.blunder_count > 0 ? (
                      <span className="text-red-400 font-medium">{g.blunder_count}</span>
                    ) : (
                      <span className="text-gray-600">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {g.mistake_count > 0 ? (
                      <span className="text-yellow-400 font-medium">{g.mistake_count}</span>
                    ) : (
                      <span className="text-gray-600">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-800">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 rounded text-sm text-gray-300 transition-colors"
            >
              Previous
            </button>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <span>Page</span>
              <input
                type="number"
                min={1}
                max={totalPages}
                value={page}
                onChange={(e) => {
                  const val = parseInt(e.target.value, 10);
                  if (!isNaN(val) && val >= 1 && val <= totalPages) setPage(val);
                }}
                className="w-14 bg-gray-800 border border-gray-700 rounded px-2 py-0.5 text-center text-white focus:outline-none focus:border-blue-500"
              />
              <span>of {totalPages}</span>
            </div>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-40 rounded text-sm text-gray-300 transition-colors"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
