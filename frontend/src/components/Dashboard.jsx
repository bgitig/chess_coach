import { useEffect, useState } from "react";
import { getWeaknesses } from "../api/client.js";
import WeaknessCard from "./WeaknessCard.jsx";

export default function Dashboard({ username }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!username) return;
    setLoading(true);
    setError(null);
    getWeaknesses(username)
      .then(setData)
      .catch((err) => {
        const detail = err.response?.data?.detail || err.message;
        setError(detail);
      })
      .finally(() => setLoading(false));
  }, [username]);

  if (!username) {
    return (
      <div className="text-center py-20 text-gray-500">
        <span className="text-5xl block mb-4">♟</span>
        <p className="text-lg">Enter your Chess.com username above to get started.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-20 text-gray-400">
        <div className="animate-spin text-4xl mb-4">⟳</div>
        <p>Loading your weakness analysis...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-20 text-red-400">
        <p className="text-lg">Error: {error}</p>
        <p className="text-gray-500 mt-2">Make sure you've synced your games first.</p>
      </div>
    );
  }

  if (!data || !data.weaknesses.length) {
    return (
      <div className="text-center py-20 text-gray-500">
        <span className="text-5xl block mb-4">📊</span>
        <p className="text-lg">No analysis data yet.</p>
        <p className="mt-2">Sync your games and wait for analysis to complete.</p>
      </div>
    );
  }

  const topWeakness = data.weaknesses[0];

  return (
    <div>
      {/* Summary header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white">
          Weakness Analysis
          <span className="text-gray-400 font-normal text-lg ml-2">— {username}</span>
        </h2>
        <p className="text-gray-400 mt-1">
          Based on {topWeakness.game_count} analyzed game
          {topWeakness.game_count !== 1 ? "s" : ""}. Sorted by severity — focus on the top items first.
        </p>
      </div>

      {/* Weakness cards */}
      <div className="grid gap-4">
        {data.weaknesses.map((w) => (
          <WeaknessCard key={w.category} weakness={w} username={username} />
        ))}
      </div>
    </div>
  );
}
