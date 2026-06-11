import { useEffect, useState, useRef } from "react";
import { getAnalysisStatus } from "../api/client.js";

export default function AnalysisProgress({ jobId, onComplete }) {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!jobId) return;

    const poll = async () => {
      try {
        const data = await getAnalysisStatus(jobId);
        setStatus(data);
        if (data.status === "complete") {
          clearInterval(intervalRef.current);
          onComplete?.();
        }
      } catch (err) {
        setError("Failed to fetch analysis status.");
        clearInterval(intervalRef.current);
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 2000);
    return () => clearInterval(intervalRef.current);
  }, [jobId]);

  if (!jobId) return null;
  if (error) return <p className="text-red-400 text-sm mt-2">{error}</p>;
  if (!status) return <p className="text-gray-400 text-sm mt-2">Loading analysis status...</p>;

  const { games_done, games_total, games_failed, status: jobStatus } = status;
  const percent = games_total > 0 ? Math.round((games_done / games_total) * 100) : 0;

  return (
    <div className="mt-4 p-4 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-gray-200">
          {jobStatus === "complete" ? "Analysis complete!" : "Analyzing games..."}
        </span>
        <span className="text-sm text-gray-400">
          {games_done}/{games_total} games
          {games_failed > 0 && (
            <span className="text-red-400 ml-2">({games_failed} failed)</span>
          )}
        </span>
      </div>
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-300 ${
            jobStatus === "complete" ? "bg-green-500" : "bg-blue-500"
          }`}
          style={{ width: `${percent}%` }}
        />
      </div>
      {jobStatus === "complete" && (
        <p className="text-green-400 text-sm mt-2">
          Done! Reload the dashboard to see your updated weakness analysis.
        </p>
      )}
    </div>
  );
}
