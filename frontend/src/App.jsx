import { useEffect, useState } from "react";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/")
      .then(res => res.json())
      .then(data => setMessage(data.message))
      .catch(() => setMessage("Failed to fetch from Django"));
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "3rem" }}>
      <h1>{message}</h1>
      <p>React + Vite + Django REST are communicating successfully.</p>
    </div>
  );
}

export default App;
