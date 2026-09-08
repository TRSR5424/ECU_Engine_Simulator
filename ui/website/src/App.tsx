import { FormEvent, useState } from "react";

type ApiValue = string | number | boolean | null | ApiValue[] | { [key: string]: ApiValue };
type ApiResponse = Record<string, ApiValue>;

async function requestJson(path: string, init?: RequestInit): Promise<ApiResponse> {
  const response = await fetch(path, init);

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as ApiResponse;
}

function stringify(value: unknown): string {
  if (typeof value === "string") {
    return value;
  }

  return JSON.stringify(value, null, 2);
}

function ResponsePanel({ title, value }: { title: string; value: string }) {
  return (
    <details className="response-panel" open={value !== "Not loaded"}>
      <summary>{title}</summary>
      <pre>{value}</pre>
    </details>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <label className="field">
      <span>{label}</span>
      {hint && <small>{hint}</small>}
      {children}
    </label>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");
  const [websiteHealth, setWebsiteHealth] = useState("Not loaded");
  const [controlHealth, setControlHealth] = useState("Not loaded");
  const [controlStatus, setControlStatus] = useState("Not loaded");
  const [controlVersion, setControlVersion] = useState("Not loaded");
  const [scripts, setScripts] = useState("Not loaded");
  const [settings, setSettings] = useState("Not loaded");
  const [results, setResults] = useState("Not loaded");
  const [message, setMessage] = useState("Ready.");
  const [scriptName, setScriptName] = useState("simulation");
  const [configName, setConfigName] = useState("");
  const [experimentName, setExperimentName] = useState("");
  const [graphType, setGraphType] = useState("");
  const [echoMessage, setEchoMessage] = useState("Hello from the website");
  const [queryMessage, setQueryMessage] = useState("Hello from query");
  const [rawJson, setRawJson] = useState('{\n  "active_experiment": "default"\n}');
  const [experimentJson, setExperimentJson] = useState('{\n  "scenario": {}\n}');
  const [compareEnabled, setCompareEnabled] = useState(false);

  async function loadOverview() {
    try {
      const [website, controlHealthResponse, controlStatusResponse, controlVersionResponse] = await Promise.all([
        requestJson("/api/health"),
        requestJson("/api/control/health"),
        requestJson("/api/control/status"),
        requestJson("/api/control/version"),
      ]);

      setWebsiteHealth(stringify(website));
      setControlHealth(stringify(controlHealthResponse));
      setControlStatus(stringify(controlStatusResponse));
      setControlVersion(stringify(controlVersionResponse));
      setMessage("Loaded API overview.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadScripts() {
    try {
      const data = await requestJson("/api/control/scripts");
      setScripts(stringify(data));
      setMessage("Loaded scripts.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function runSelectedScript(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      const data = await requestJson(`/api/control/scripts/run/${encodeURIComponent(scriptName)}`);
      setMessage(stringify(data));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function runAllScripts() {
    try {
      const data = await requestJson("/api/control/scripts/runall");
      setMessage(stringify(data));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadSettings() {
    try {
      const query = configName.trim() ? `?config_name=${encodeURIComponent(configName.trim())}` : "";
      const data = await requestJson(`/api/control/settings${query}`);
      setSettings(stringify(data));
      setMessage("Loaded settings.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function updateGlobalSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    try {
      const parsed = JSON.parse(rawJson) as ApiResponse;
      const data = await requestJson("/api/control/settings/updateGlobal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parsed),
      });
      setMessage(stringify(data));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Invalid JSON or request failed");
    }
  }

  async function saveExperiment(operation: "newExperiment" | "update") {
    if (!experimentName.trim()) {
      setMessage("Enter an experiment name first.");
      return;
    }
    try {
      const data = await requestJson(`/api/control/settings/${operation}/${encodeURIComponent(experimentName.trim())}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: experimentJson,
      });
      setSettings(stringify(data));
      setMessage(`${operation === "newExperiment" ? "Created" : "Updated"} experiment.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Invalid JSON or request failed");
    }
  }

  async function compareSettings() {
    try {
      const data = await requestJson(`/api/control/settings/compare?experiment_name=${encodeURIComponent(experimentName.trim())}`);
      setSettings(stringify(data));
      setMessage("Loaded settings comparison.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function saveCompareMode() {
    try {
      const data = await requestJson(`/api/control/settings/setCompare/${compareEnabled}`, { method: "POST" });
      setSettings(stringify(data));
      setMessage("Comparison mode updated.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadResults() {
    try {
      const query = experimentName.trim() ? `?experiment_name=${encodeURIComponent(experimentName.trim())}` : "";
      const data = await requestJson(`/api/control/results${query}`);
      setResults(stringify(data));
      setMessage("Loaded results.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadExperimentResults() {
    try {
      const query = experimentName.trim() ? `?experiment_name=${encodeURIComponent(experimentName.trim())}` : "";
      const data = await requestJson(`/api/control/results/experiments${query}`);
      setResults(stringify(data));
      setMessage("Loaded experiment results.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadCsvResults() {
    try {
      const query = experimentName.trim() ? `?experiment_name=${encodeURIComponent(experimentName.trim())}` : "";
      const data = await requestJson(`/api/control/results/csv${query}`);
      setResults(stringify(data));
      setMessage("Loaded CSV results.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function loadGraphResults() {
    try {
      const params = new URLSearchParams();
      if (experimentName.trim()) {
        params.set("experiment_name", experimentName.trim());
      }
      if (graphType.trim()) {
        params.set("graph_type", graphType.trim());
      }
      const query = params.toString() ? `?${params.toString()}` : "";
      const data = await requestJson(`/api/control/results/graph${query}`);
      setResults(stringify(data));
      setMessage("Loaded graph results.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  async function callControlPath(path: string) {
    try {
      const data = await requestJson(path);
      setMessage(stringify(data));
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Unknown error");
    }
  }

  const tabs = [
    ["overview", "Overview"],
    ["scripts", "Run scripts"],
    ["settings", "Settings"],
    ["results", "Results"],
    ["diagnostics", "Diagnostics"],
  ];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-mark">ECU</div>
        <div>
          <p className="eyebrow">Control center</p>
          <h1>Engine simulator</h1>
        </div>
        <nav aria-label="Main navigation">
          {tabs.map(([id, label]) => (
            <button className={activeTab === id ? "nav-item active" : "nav-item"} key={id} onClick={() => setActiveTab(id)} type="button">
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" />
          <span>{message}</span>
        </div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Development workspace</p>
            <h2>{tabs.find(([id]) => id === activeTab)?.[1]}</h2>
          </div>
          <button className="button primary" onClick={() => void loadOverview()} type="button">Refresh API</button>
        </header>

        {activeTab === "overview" && (
          <div className="page-content">
            <div className="intro">
              <div><p className="eyebrow">Live system view</p><h3>Keep an eye on the simulator.</h3><p>Check the services, launch a run, and inspect its output from one place.</p></div>
              <button className="button primary" onClick={() => void loadOverview()} type="button">Check connection</button>
            </div>
            <div className="metric-grid">
              <div className="metric-card"><span>Website API</span><strong>{websiteHealth === "Not loaded" ? "Not checked" : "Online"}</strong><small>{websiteHealth === "Not loaded" ? "Run a connection check" : websiteHealth}</small></div>
              <div className="metric-card"><span>Control API</span><strong>{controlHealth === "Not loaded" ? "Not checked" : "Online"}</strong><small>{controlStatus}</small></div>
              <div className="metric-card"><span>Version</span><strong>{controlVersion === "Not loaded" ? "—" : controlVersion.replace(/[{}\"]+/g, "").replace("version:", "")}</strong><small>Current control service</small></div>
            </div>
            <div className="content-grid"><div className="panel"><div className="panel-heading"><div><p className="eyebrow">Quick start</p><h3>Common actions</h3></div></div><div className="quick-actions"><button className="action-card" onClick={() => { setActiveTab("scripts"); void loadScripts(); }} type="button"><strong>Run a script</strong><span>Start simulation or analysis</span></button><button className="action-card" onClick={() => { setActiveTab("results"); void loadResults(); }} type="button"><strong>View results</strong><span>Browse experiments and output</span></button><button className="action-card" onClick={() => { setActiveTab("settings"); void loadSettings(); }} type="button"><strong>Inspect settings</strong><span>Load the active configuration</span></button></div></div><ResponsePanel title="Connection details" value={[websiteHealth, controlHealth, controlStatus, controlVersion].join("\n\n")} /></div>
          </div>
        )}

        {activeTab === "scripts" && <div className="page-content"><div className="page-title"><p className="eyebrow">Simulation pipeline</p><h3>Run scripts</h3><p>Use the active configuration to generate simulation data, analysis, or comparisons.</p></div><div className="content-grid"><div className="panel"><div className="button-row"><button className="button" onClick={() => void loadScripts()} type="button">Load available scripts</button><button className="button primary" onClick={() => void runAllScripts()} type="button">Run all scripts</button></div><form onSubmit={runSelectedScript}><Field hint="Try simulation, analysis, or compare_runs" label="Script name"><input value={scriptName} onChange={(event) => setScriptName(event.target.value)} /></Field><button className="button primary" type="submit">Run selected script</button></form></div><ResponsePanel title="Script response" value={scripts} /></div></div>}

        {activeTab === "settings" && <div className="page-content"><div className="page-title"><p className="eyebrow">Configuration</p><h3>Shape the next run</h3><p>Load, update, compare, or create experiment configurations.</p></div><div className="content-grid"><div className="panel"><form onSubmit={(event) => { event.preventDefault(); void loadSettings(); }}><Field hint="Leave empty to load the active experiment" label="Config or experiment name"><input value={configName} onChange={(event) => setConfigName(event.target.value)} /></Field><button className="button" type="submit">Load settings</button></form><hr /><form onSubmit={updateGlobalSettings}><Field label="Global settings JSON" hint="A JSON object matching the global configuration"><textarea rows={7} value={rawJson} onChange={(event) => setRawJson(event.target.value)} /></Field><button className="button primary" type="submit">Update global settings</button></form><hr /><Field label="Experiment name"><input value={experimentName} onChange={(event) => setExperimentName(event.target.value)} /></Field><Field label="Experiment sections JSON"><textarea rows={7} value={experimentJson} onChange={(event) => setExperimentJson(event.target.value)} /></Field><div className="button-row"><button className="button" onClick={() => void saveExperiment("newExperiment")} type="button">Create experiment</button><button className="button" onClick={() => void saveExperiment("update")} type="button">Update experiment</button><button className="button" onClick={() => void compareSettings()} type="button">Compare</button></div><label className="check-field"><input checked={compareEnabled} onChange={(event) => setCompareEnabled(event.target.checked)} type="checkbox" /> Comparison mode</label><button className="button" onClick={() => void saveCompareMode()} type="button">Save comparison mode</button></div><ResponsePanel title="Settings response" value={settings} /></div></div>}

        {activeTab === "results" && <div className="page-content"><div className="page-title"><p className="eyebrow">Output explorer</p><h3>Results and visualisation</h3><p>Inspect generated files, preview CSV data, and find graph outputs.</p></div><div className="panel"><div className="form-grid"><Field label="Experiment name"><input value={experimentName} onChange={(event) => setExperimentName(event.target.value)} /></Field><Field label="Graph filter" hint="Optional filename filter"><input value={graphType} onChange={(event) => setGraphType(event.target.value)} /></Field></div><div className="button-row"><button className="button primary" onClick={() => void loadResults()} type="button">Summary</button><button className="button" onClick={() => void loadExperimentResults()} type="button">Experiment files</button><button className="button" onClick={() => void loadCsvResults()} type="button">CSV preview</button><button className="button" onClick={() => void loadGraphResults()} type="button">Graph files</button></div></div><ResponsePanel title="Results response" value={results} /></div>}

        {activeTab === "diagnostics" && <div className="page-content"><div className="page-title"><p className="eyebrow">Service diagnostics</p><h3>Test the connection</h3><p>Call the lower-level routes directly when troubleshooting the control API.</p></div><div className="panel"><div className="form-grid"><Field label="Path message"><input value={echoMessage} onChange={(event) => setEchoMessage(event.target.value)} /></Field><Field label="Query message"><input value={queryMessage} onChange={(event) => setQueryMessage(event.target.value)} /></Field></div><div className="button-row"><button className="button" onClick={() => void callControlPath(`/api/control/echo/path/${encodeURIComponent(echoMessage)}`)} type="button">Echo path</button><button className="button" onClick={() => void callControlPath(`/api/control/echo/query?message=${encodeURIComponent(queryMessage)}`)} type="button">Echo query</button><button className="button" onClick={() => void callControlPath("/api/control/secure-data")} type="button">Secure data</button><button className="button" onClick={() => void callControlPath("/api/control/other/secure-info")} type="button">Secure info</button></div></div><ResponsePanel title="Latest response" value={message} /></div>}
      </section>
    </main>
  );
}