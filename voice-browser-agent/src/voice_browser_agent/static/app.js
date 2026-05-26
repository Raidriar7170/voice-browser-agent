const state = {
  executionId: null,
  trace: null,
  recorder: null,
  chunks: [],
};

const $ = (id) => document.getElementById(id);

function showJson(id, value) {
  $(id).textContent = JSON.stringify(value, null, 2);
}

function renderTrace(trace) {
  state.trace = trace;
  state.executionId = trace.execution_id;
  $("transcriptPanel").textContent = trace.transcript?.text || "";
  showJson("normalizedPanel", trace.normalized_output || {});
  showJson("tracePanel", trace);
  const timeline = $("timeline");
  timeline.innerHTML = "";
  for (const action of trace.browser_actions || []) {
    const item = document.createElement("li");
    item.textContent = `${action.action_type}: ${action.description}`;
    timeline.appendChild(item);
  }
  const pending = trace.confirmation_decision?.state === "pending";
  $("confirmation").classList.toggle("hidden", !pending);
  $("confirmationReason").textContent = trace.confirmation_decision?.reason || "";
  $("uploadStatus").textContent = `Status: ${trace.final_status || "unknown"}`;
}

function renderError(error) {
  $("uploadStatus").textContent = error.message || String(error);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

$("uploadForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = $("audioFile").files[0];
  if (!file) {
    $("uploadStatus").textContent = "Choose an audio file or type a transcript.";
    return;
  }
  const data = new FormData();
  data.append("file", file);
  const response = await fetch("/api/ingest", { method: "POST", body: data });
  $("uploadStatus").textContent = response.ok ? "Audio accepted." : await response.text();
});

$("runButton").addEventListener("click", async () => {
  try {
    const transcript = $("transcriptInput").value.trim();
    const trace = await postJson("/api/executions", { transcript_text: transcript });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("fixtureRunButton").addEventListener("click", async () => {
  try {
    const fixtureId = $("fixtureSelect").value;
    const trace = await postJson(`/api/fixtures/${fixtureId}/executions`, {});
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("confirmButton").addEventListener("click", async () => {
  if (!state.executionId) return;
  try {
    renderTrace(
      await postJson(`/api/executions/${state.executionId}/confirmation`, {
        decision: "confirm",
        decided_by: "operator",
      }),
    );
  } catch (error) {
    renderError(error);
  }
});

$("cancelButton").addEventListener("click", async () => {
  if (!state.executionId) return;
  try {
    renderTrace(
      await postJson(`/api/executions/${state.executionId}/confirmation`, {
        decision: "cancel",
        decided_by: "operator",
      }),
    );
  } catch (error) {
    renderError(error);
  }
});

$("exportButton").addEventListener("click", async () => {
  if (!state.executionId) return;
  try {
    const response = await fetch(`/api/traces/${state.executionId}/export`);
    showJson("tracePanel", await response.json());
  } catch (error) {
    renderError(error);
  }
});

$("recordButton").addEventListener("click", async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    $("uploadStatus").textContent = "Recording is unavailable in this browser.";
    return;
  }
  if (state.recorder?.state === "recording") {
    state.recorder.stop();
    return;
  }
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  state.chunks = [];
  state.recorder = new MediaRecorder(stream);
  state.recorder.ondataavailable = (event) => state.chunks.push(event.data);
  state.recorder.onstop = async () => {
    const blob = new Blob(state.chunks, { type: "audio/webm" });
    const data = new FormData();
    data.append("file", blob, "recording.webm");
    const response = await fetch("/api/recordings", { method: "POST", body: data });
    $("uploadStatus").textContent = response.ok ? "Recording accepted." : await response.text();
    stream.getTracks().forEach((track) => track.stop());
  };
  state.recorder.start();
  $("uploadStatus").textContent = "Recording one command...";
});
