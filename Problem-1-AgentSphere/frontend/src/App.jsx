import { useCallback, useEffect, useState } from "react";
import { Play, Square, Activity, RefreshCw, AlertCircle } from "lucide-react";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import NetworkFeed from "./pages/NetworkFeed";
import RoutingInspector from "./pages/RoutingInspector";
import AgentDirectory from "./pages/AgentDirectory";
import Analytics from "./pages/Analytics";
import { api } from "./services/api";
import "./App.css";

export default function App() {
  const [activePage, setActivePage] = useState("Network Feed");

  const [simulationStatus, setSimulationStatus] = useState("STOPPED");
  const [simulationLoading, setSimulationLoading] = useState(false);
  const [simulationError, setSimulationError] = useState("");

  const loadSimulationStatus = useCallback(async () => {
    try {
      const data = await api.getSimulationStatus();
      setSimulationStatus(data.simulation_status || "STOPPED");
      setSimulationError("");
    } catch (err) {
      setSimulationError(err.message || "Unable to get simulation status.");
    }
  }, []);

  useEffect(() => {
    loadSimulationStatus();
  }, [loadSimulationStatus]);

  async function handleSimulation(action) {
    setSimulationLoading(true);
    setSimulationError("");

    try {
      if (action === "start") {
        await api.startSimulation();
      } else {
        await api.stopSimulation();
      }

      await loadSimulationStatus();
    } catch (err) {
      setSimulationError(err.message || "Unable to update simulation.");
    } finally {
      setSimulationLoading(false);
    }
  }

  function renderPage() {
    switch (activePage) {
      case "Network Feed":
        return <NetworkFeed />;

      case "Routing Inspector":
        return <RoutingInspector />;

      case "Agent Directory":
        return <AgentDirectory />;

      case "Analytics":
        return <Analytics />;

      default:
        return (
          <div className="panel coming-soon">
            <h3>{activePage}</h3>
            <p>This workspace is coming in the next implementation step.</p>
          </div>
        );
    }
  }

  return (
    <div className="app-layout">
      <Sidebar activePage={activePage} onNavigate={setActivePage} />

      <main className="main-content">
        <Topbar
          activePage={activePage}
          onRefresh={() => window.location.reload()}
        />

        <div className="simulation-toolbar">
          <div className="simulation-info">
            <div className="simulation-icon">
              <Activity size={18} />
            </div>

            <div>
              <strong>Agent Simulation</strong>
              <span className="simulation-status">
                <span
                  className={`simulation-indicator ${
                    simulationStatus === "RUNNING" ? "running" : "stopped"
                  }`}
                />
                {simulationStatus}
              </span>
            </div>
          </div>

          <div className="simulation-actions">
            <button
              className="button primary"
              onClick={() => handleSimulation("start")}
              disabled={simulationLoading || simulationStatus === "RUNNING"}
            >
              <Play size={15} />
              Start
            </button>

            <button
              className="button secondary"
              onClick={() => handleSimulation("stop")}
              disabled={simulationLoading || simulationStatus === "STOPPED"}
            >
              <Square size={14} />
              Stop
            </button>

            <button
              className="button secondary"
              onClick={loadSimulationStatus}
              disabled={simulationLoading}
              title="Refresh simulation status"
            >
              <RefreshCw size={15} />
            </button>
          </div>
        </div>

        {simulationError && (
          <div className="feedback-message error">
            <AlertCircle size={15} />
            {simulationError}
          </div>
        )}

        <div className="page-container">{renderPage()}</div>
      </main>
    </div>
  );
}
