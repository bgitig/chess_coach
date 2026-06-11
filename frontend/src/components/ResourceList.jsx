import { useEffect, useState } from "react";
import { getResources, completeResource } from "../api/client.js";

const TYPE_ICONS = {
  tool: "🔧",
  video: "🎬",
  course: "📚",
  book: "📖",
};

export default function ResourceList({ category, username }) {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!category || !username) return;
    setLoading(true);
    getResources(category, username)
      .then((data) => setResources(data.resources))
      .catch(() => setError("Failed to load resources."))
      .finally(() => setLoading(false));
  }, [category, username]);

  const toggle = async (resourceId) => {
    if (!username) return;
    try {
      const result = await completeResource(resourceId, username);
      setResources((prev) =>
        prev.map((r) =>
          r.id === resourceId ? { ...r, completed: result.completed } : r
        )
      );
    } catch {
      // ignore
    }
  };

  if (loading) return <p className="text-gray-500 text-sm">Loading resources...</p>;
  if (error) return <p className="text-red-400 text-sm">{error}</p>;
  if (!resources.length) return <p className="text-gray-500 text-sm">No resources available.</p>;

  return (
    <ul className="space-y-2 mt-3">
      {resources.map((r) => (
        <li key={r.id} className="flex items-start gap-3">
          <button
            onClick={() => toggle(r.id)}
            className={`mt-0.5 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
              r.completed
                ? "bg-green-600 border-green-600"
                : "border-gray-600 hover:border-gray-400"
            }`}
            title={r.completed ? "Mark incomplete" : "Mark complete"}
          >
            {r.completed && <span className="text-white text-xs font-bold">✓</span>}
          </button>
          <div className="flex-1">
            <a
              href={r.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`text-sm font-medium transition-colors hover:underline ${
                r.completed
                  ? "line-through text-gray-500"
                  : "text-blue-400 hover:text-blue-300"
              }`}
            >
              <span className="mr-1">{TYPE_ICONS[r.type] || "🔗"}</span>
              {r.title}
            </a>
            <p className={`text-xs mt-0.5 ${r.completed ? "text-gray-600" : "text-gray-400"}`}>
              {r.description}
            </p>
          </div>
        </li>
      ))}
    </ul>
  );
}
