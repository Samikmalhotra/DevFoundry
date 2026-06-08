const API_BASE = window.location.origin;

async function runCrew(requirements, uiFramework) {
  const response = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ requirements, ui_framework: uiFramework })
  });
  if (!response.ok) {
    throw new Error(`Failed to start run: ${response.statusText}`);
  }
  return response.json();
}

async function fetchWorkflow() {
  const response = await fetch(`${API_BASE}/workflow`);
  if (!response.ok) {
    throw new Error(`Failed to fetch workflow: ${response.statusText}`);
  }
  return response.json();
}

async function fetchArtifacts(runId = "") {
  const url = runId ? `${API_BASE}/artifacts?run_id=${runId}` : `${API_BASE}/artifacts`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch artifacts: ${response.statusText}`);
  }
  return response.json();
}

async function fetchArtifactContent(path, runId = "") {
  const url = runId ? `${API_BASE}/artifact/${path}?run_id=${runId}` : `${API_BASE}/artifact/${path}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch artifact content: ${response.statusText}`);
  }
  return response.json();
}

async function fetchRuns() {
  const response = await fetch(`${API_BASE}/runs`);
  if (!response.ok) {
    throw new Error(`Failed to fetch runs: ${response.statusText}`);
  }
  return response.json();
}

async function fetchRunDetails(runId) {
  const response = await fetch(`${API_BASE}/runs/${runId}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch run details: ${response.statusText}`);
  }
  return response.json();
}

async function killRun(runId) {
  const response = await fetch(`${API_BASE}/runs/${runId}/kill`, {
    method: "POST"
  });
  if (!response.ok) {
    throw new Error(`Failed to kill run: ${response.statusText}`);
  }
  return response.json();
}
