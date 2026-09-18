import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/health")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend returned an error");
        }

        return response.json();
      })
      .then((data) => {
        if (data.status === "ok") {
          setBackendStatus("Connected");
        } else {
          setBackendStatus("Unexpected response");
        }
      })
      .catch(() => {
        setBackendStatus("Disconnected");
      });
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-mark"> M </span>
          <span>MANTIS</span>
        </div>

        <nav>
          <button className="nav-item active">Dashboard</button>
          <button className="nav-item">Agents</button>
          <button className="nav-item">Workflows</button>
          <button className="nav-item">Models</button>
          <button className="nav-item">Settings</button>
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <h1>Dashboard</h1>
        </header>

        <section className="content">
          <div className="welcome">
            <p className="eyebrow">AI AGENT PLATFORM</p>

            <h2>Welcome to MANTIS</h2>

            <p>
              Build, configure, and run AI agents from one Windows desktop
              application.
            </p>

            <div className="status">
              <span className="status-dot"></span>
              Agent Runtime: <strong>{backendStatus}</strong>
            </div>

            <button className="primary-button">
              Create your first agent
            </button>
          </div>

          <div className="cards">
            <div className="card">
              <h3>Agents</h3>
              <p>Create and manage your AI agents.</p>
            </div>

            <div className="card">
              <h3>Workflows</h3>
              <p>Design workflows that connect AI, tools, and logic.</p>
            </div>

            <div className="card">
              <h3>Models</h3>
              <p>Connect local and cloud AI models.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;