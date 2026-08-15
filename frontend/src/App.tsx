import { NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Chat from "./pages/Chat";

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <img src="/logos/lokt-light.png" alt="Lokt" className="brand" />
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Dashboard
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => (isActive ? "active" : "")}>
            Chat
          </NavLink>
        </nav>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </main>
    </div>
  );
}
