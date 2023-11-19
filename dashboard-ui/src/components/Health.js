import React, { useEffect, useState } from "react";
import "../App.css";

export default function Health() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [stats, setStats] = useState({});
  const [error, setError] = useState(null);

  const getStats = () => {
    fetch(`http://20.151.78.202:8120/health`)
      .then((res) => res.json())
      .then(
        (result) => {
          console.log("Received Health");
          setStats(result);
          setIsLoaded(true);
        },
        (error) => {
          setError(error);
          setIsLoaded(true);
        }
      );
  };
  useEffect(() => {
    const interval = setInterval(() => getStats(), 2000);
    return () => clearInterval(interval);
  }, [getStats]);

  if (error) {
    return (
      <div className={"error"}>
        Error found when fetching from API {JSON.stringify(error)}
      </div>
    );
  } else if (isLoaded === false) {
    return <div>Loading...</div>;
  } else if (isLoaded === true) {
    return (
      <div>
        <table className="StatsTable">
          <tbody>
            <tr>
              <th>Service</th>
              <th>Health</th>
            </tr>
            <tr>
              <td>Receiver:</td>
              <td
                style={{
                  fontWeight: "bold",
                  color: stats["receiver"] === "Running" ? "green" : "red",
                }}
              >
                {stats["receiver"]}
              </td>
            </tr>
            <tr>
              <td>Storage:</td>
              <td
                style={{
                  fontWeight: "bold",
                  color: stats["storage"] === "Running" ? "green" : "red",
                }}
              >
                {stats["storage"]}
              </td>
            </tr>
            <tr>
              <td>Processing:</td>
              <td
                style={{
                  fontWeight: "bold",
                  color: stats["processing"] === "Running" ? "green" : "red",
                }}
              >
                {stats["processing"]}
              </td>
            </tr>
            <tr>
              <td>Audit:</td>
              <td
                style={{
                  fontWeight: "bold",
                  color: stats["audit"] === "Running" ? "green" : "red",
                }}
              >
                {stats["audit"]}
              </td>
            </tr>
            <tr>
              <td>Last Updated:</td>
              <td style={{ fontWeight: "bold" }}>
                {new Date().getSeconds() -
                  new Date(stats["last_update"].slice(0, 23)).getSeconds()}{" "}
                seconds ago
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }
}
