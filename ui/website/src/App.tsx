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

export default function App() {
  const [websiteHealth, setWebsiteHealth] = useState("Not loaded");
  const [controlHealth, setControlHealth] = useState("Not loaded");
  const [controlStatus, setControlStatus] = useState("Not loaded");
  const [controlVersion, setControlVersion] = useState("Not loaded");
  const [scripts, setScripts] = useState("Not loaded");
  const [settings, setSettings] = useState("Not loaded");
  const [results, setResults] = useState("Not loaded");
  const [message, setMessage] = useState("Ready.");

  const [scriptName, setScriptName] = useState("");
  const [configName, setConfigName] = useState("");
  const [experimentName, setExperimentName] = useState("");
  const [graphType, setGraphType] = useState("");
  const [echoMessage, setEchoMessage] = useState("Hello from the website");
  const [queryMessage, setQueryMessage] = useState("Hello from query");
  const [rawJson, setRawJson] = useState('{"example": true}');

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

  return (
    <main>
      <header>
        <h1>ECU Engine Simulator</h1>
        <p>Plain React control panel for the simulator APIs.</p>
      </header>

      <section>
        <h2>API Overview</h2>
        <button type="button" onClick={loadOverview}>
          Load API overview
        </button>
        <pre>{websiteHealth}</pre>
        <pre>{controlHealth}</pre>
        <pre>{controlStatus}</pre>
        <pre>{controlVersion}</pre>
      </section>

      <section>
        <h2>Scripts</h2>
        <button type="button" onClick={loadScripts}>
          Load scripts
        </button>
        <button type="button" onClick={runAllScripts}>
          Run all scripts
        </button>
        <form onSubmit={runSelectedScript}>
          <label>
            Script name
            <input value={scriptName} onChange={(event) => setScriptName(event.target.value)} />
          </label>
          <button type="submit">Run script</button>
        </form>
        <pre>{scripts}</pre>
      </section>

      <section>
        <h2>Settings</h2>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void loadSettings();
          }}
        >
          <label>
            Config name
            <input value={configName} onChange={(event) => setConfigName(event.target.value)} />
          </label>
          <button type="submit">Load settings</button>
        </form>
        <form onSubmit={updateGlobalSettings}>
          <label>
            JSON payload
            <textarea rows={8} value={rawJson} onChange={(event) => setRawJson(event.target.value)} />
          </label>
          <button type="submit">Update global settings</button>
        </form>
        <pre>{settings}</pre>
      </section>

      <section>
        <h2>Results</h2>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void loadResults();
          }}
        >
          <label>
            Experiment name
            <input value={experimentName} onChange={(event) => setExperimentName(event.target.value)} />
          </label>
          <button type="submit">Load results</button>
        </form>
        <button type="button" onClick={loadExperimentResults}>
          Load experiment results
        </button>
        <button type="button" onClick={loadCsvResults}>
          Load CSV results
        </button>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            void loadGraphResults();
          }}
        >
          <label>
            Graph type
            <input value={graphType} onChange={(event) => setGraphType(event.target.value)} />
          </label>
          <button type="submit">Load graph results</button>
        </form>
        <pre>{results}</pre>
      </section>

      <section>
        <h2>Control Endpoints</h2>
        <label>
          Echo message
          <input value={echoMessage} onChange={(event) => setEchoMessage(event.target.value)} />
        </label>
        <label>
          Query message
          <input value={queryMessage} onChange={(event) => setQueryMessage(event.target.value)} />
        </label>
        <button type="button" onClick={() => void callControlPath(`/api/control/echo/path/${encodeURIComponent(echoMessage)}`)}>
          Call echo/path
        </button>
        <button type="button" onClick={() => void callControlPath(`/api/control/echo/query?message=${encodeURIComponent(queryMessage)}`)}>
          Call echo/query
        </button>
        <button type="button" onClick={() => void callControlPath("/api/control/secure-data") }>
          Call secure data
        </button>
        <button type="button" onClick={() => void callControlPath("/api/control/other/secure-info") }>
          Call secure info
        </button>
      </section>

      <section>
        <h2>Status</h2>
        <pre>{message}</pre>
      </section>
    </main>
  );
}