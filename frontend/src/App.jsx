import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard.jsx";
import GameLibrary from "./components/GameLibrary.jsx";
import SyncPanel from "./components/SyncPanel.jsx";
import { useState } from "react";

export default function App() {
  const [username, setUsername] = useState(() => localStorage.getItem("chess_username") || "");

  const handleUsernameSet = (u) => {
    setUsername(u);
    localStorage.setItem("chess_username", u);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">♟</span>
              <h1 className="text-xl font-bold text-white">Chess Tutor</h1>
            </div>
            <nav className="flex gap-1">
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-gray-400 hover:text-white hover:bg-gray-800"
                  }`
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/games"
                className={({ isActive }) =>
                  `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-gray-400 hover:text-white hover:bg-gray-800"
                  }`
                }
              >
                Game Library
              </NavLink>
            </nav>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-6xl mx-auto px-6 py-8">
          <SyncPanel username={username} onUsernameChange={handleUsernameSet} />

          <Routes>
            <Route path="/" element={<Dashboard username={username} />} />
            <Route path="/games" element={<GameLibrary username={username} />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
