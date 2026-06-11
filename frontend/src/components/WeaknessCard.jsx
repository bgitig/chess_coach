import { useState } from "react";
import ResourceList from "./ResourceList.jsx";

const CATEGORY_LABELS = {
  opening: "Opening Preparation",
  tactics: "Tactical Awareness",
  endgame: "Endgame Technique",
  positional: "Positional Play",
  time_management: "Time Management",
};

const CATEGORY_DESCRIPTIONS = {
  opening: "You're making significant errors in the first 15 moves. Focus on learning opening principles and key variations for your repertoire.",
  tactics: "You're missing tactical opportunities and falling into tactical traps. Daily puzzle practice is the fastest way to improve.",
  endgame: "You're struggling to convert or defend endgame positions. Study fundamental endgame techniques to win more won games.",
  positional: "You're making strategic mistakes in the middlegame. Work on understanding pawn structures and piece activity.",
  time_management: "You're frequently running low on time, leading to poor decisions late in games. Practice playing faster in lower-stakes games.",
};

const CATEGORY_ICONS = {
  opening: "📖",
  tactics: "⚡",
  endgame: "♔",
  positional: "♟",
  time_management: "⏱",
};

function SeverityBadge({ score }) {
  if (score >= 60) return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-900 text-red-300">Critical</span>;
  if (score >= 35) return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-900 text-yellow-300">Moderate</span>;
  if (score >= 10) return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-300">Minor</span>;
  return <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-700 text-gray-400">Good</span>;
}

function ScoreBar({ score }) {
  const color = score >= 60 ? "bg-red-500" : score >= 35 ? "bg-yellow-500" : score >= 10 ? "bg-blue-500" : "bg-green-500";
  return (
    <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
      <div className={`h-2 rounded-full transition-all ${color}`} style={{ width: `${score}%` }} />
    </div>
  );
}

export default function WeaknessCard({ weakness, username }) {
  const [expanded, setExpanded] = useState(false);
  const { category, score, blunder_count, mistake_count, inaccuracy_count, game_count } = weakness;
  const label = CATEGORY_LABELS[category] || category;
  const icon = CATEGORY_ICONS[category] || "📌";
  const description = CATEGORY_DESCRIPTIONS[category] || "";

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <span className="text-2xl flex-shrink-0">{icon}</span>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="font-semibold text-white">{label}</h3>
              <SeverityBadge score={score} />
            </div>
            <p className="text-sm text-gray-400 mt-0.5">{description}</p>
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-2xl font-bold text-white">{Math.round(score)}</div>
          <div className="text-xs text-gray-500">/ 100</div>
        </div>
      </div>

      <ScoreBar score={score} />

      {/* Stats */}
      <div className="flex gap-4 mt-3 text-xs text-gray-500">
        {blunder_count > 0 && (
          <span className="text-red-400">
            {blunder_count} blunder{blunder_count !== 1 ? "s" : ""}
          </span>
        )}
        {mistake_count > 0 && (
          <span className="text-yellow-400">
            {mistake_count} mistake{mistake_count !== 1 ? "s" : ""}
          </span>
        )}
        {inaccuracy_count > 0 && (
          <span className="text-blue-400">
            {inaccuracy_count} inaccurac{inaccuracy_count !== 1 ? "ies" : "y"}
          </span>
        )}
        <span>{game_count} game{game_count !== 1 ? "s" : ""} analyzed</span>
      </div>

      {/* Study button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="mt-4 w-full bg-blue-700 hover:bg-blue-600 text-white text-sm font-medium py-2 rounded-lg transition-colors"
      >
        {expanded ? "Hide Resources" : "Study Now"}
      </button>

      {/* Resources */}
      {expanded && (
        <div className="mt-4 border-t border-gray-800 pt-4">
          <p className="text-sm font-medium text-gray-300 mb-1">Recommended Resources</p>
          <ResourceList category={category} username={username} />
        </div>
      )}
    </div>
  );
}
