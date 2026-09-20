import { useState } from "react";
import "./App.css";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

function App() {
  const [backendStatus] = useState("Connected");
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const sendMessage = async () => {
    const text = message.trim();

    if (!text) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        id: Date.now(),
        role: "user",
        content: text,
      },
    ]);

    setMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: data.message,
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: "Sorry, I could not connect to the MANTIS backend.",
        },
      ]);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-mark">M</span>
          <span>MANTIS</span>
        </div>

        <button className="new-chat-button" onClick={() => setMessages([])}>
          + New Chat
        </button>

        <div className="history">
          <p className="history-title">Today</p>

          {messages.length === 0 ? (
            <p className="history-empty">No conversations yet</p>
          ) : (
            <p className="history-item">Current conversation</p>
          )}
        </div>

        <div className="sidebar-bottom">
          <button className="sidebar-button">Settings</button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <h1>MANTIS</h1>
            <p>Windows AI Assistant</p>
          </div>

          <div className="connection-status">
            <span className="status-dot"></span>
            {backendStatus}
          </div>
        </header>

        <section className="chat">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-mark">M</div>

              <h2>How can I help?</h2>

              <p>
                Ask MANTIS to work with your computer, files, information, and
                more.
              </p>

              <div className="suggestions">
                <button
                  onClick={() =>
                    setMessage(
                      "Search the internet for the latest Java features and summarize them."
                    )
                  }
                >
                  Search the web
                </button>

                <button
                  onClick={() =>
                    setMessage(
                      "Find all SAP CPI PDFs in my Documents folder and summarize them."
                    )
                  }
                >
                  Search my files
                </button>

                <button onClick={() => setMessage("Summarize this PDF.")}>
                  Summarize a document
                </button>
              </div>
            </div>
          ) : (
            <div className="messages">
              {messages.map((item) => (
                <div
                  className={`message ${
                    item.role === "user" ? "message-user" : "message-assistant"
                  }`}
                  key={item.id}
                >
                  <div className="message-role">
                    {item.role === "user" ? "You" : "MANTIS"}
                  </div>

                  <div className="message-content">{item.content}</div>
                </div>
              ))}
            </div>
          )}

          <div className="composer-container">
            <div className="composer">
              <textarea
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask MANTIS anything..."
                rows={1}
              />

              <button
                className="send-button"
                onClick={sendMessage}
                disabled={!message.trim()}
              >
                ↑
              </button>
            </div>

            <p className="composer-hint">
              Enter to send · Shift + Enter for a new line
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;