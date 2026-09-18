import { useEffect, useState } from "react";
import "./App.css";

type Agent = {
  id: number;
  name: string;
  description: string | null;
  created_at: string;
};

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [agents, setAgents] = useState<Agent[]>([]);

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
      .catch((error) => {
  console.error("Backend connection failed:", error);
  setBackendStatus(`Disconnected: ${error.message}`);
});

    fetch("http://127.0.0.1:8000/agents")
      .then((response) => response.json())
      .then((data) => {
        setAgents(data);
      })
      .catch((error) => {
        console.error("Failed to load agents:", error);
      });
  }, []);

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-mark">M</span>
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
          </div>

          <div className="cards">
            <div className="card">
              <h3>Agents</h3>
              <p>{agents.length} agent(s) available.</p>
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

          <div className="agent-list">
            <h2>Agents</h2>

            {agents.length === 0 ? (
              <p>No agents found.</p>
            ) : (
              agents.map((agent) => (
                <div className="agent-item" key={agent.id}>
                  <div>
                    <h3>{agent.name}</h3>
                    <p>{agent.description || "No description"}</p>
                  </div>

                  <span>#{agent.id}</span>
                </div>
              ))
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;