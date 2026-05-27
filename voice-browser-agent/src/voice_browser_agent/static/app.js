const state = {
  executionId: null,
  trace: null,
  recorder: null,
  chunks: [],
  audioId: null,
  fixtures: [],
  currentInputSource: null,
};

const $ = (id) => document.getElementById(id);

function showJson(id, value) {
  $(id).textContent = JSON.stringify(value, null, 2);
}

function inputSourceForTrace(trace) {
  if (state.currentInputSource) return state.currentInputSource;
  const metadata = trace.transcript?.metadata || {};
  if (metadata.adapter_name === "direct-preview") return "transcript-based execution";
  if (metadata.adapter_name === "fixture-manifest-asr") return "fixture-based execution";
  if (metadata.input_audio_id) return "audio-based execution";
  return "unknown";
}

function renderSummary(trace) {
  const mode = trace.execution_mode || trace.execution_runtime?.execution_mode || "unknown";
  const lines = [
    `Input source: ${inputSourceForTrace(trace)}`,
    `Execution mode: ${mode}`,
    `Final status: ${trace.final_status || "unknown"}`,
  ];
  if (trace.stop_reason) lines.push(`Stop reason: ${trace.stop_reason}`);
  if (trace.failure_reason) lines.push(`Failure reason: ${trace.failure_reason}`);
  if (trace.normalized_output?.kind === "clarification_request") {
    lines.push(`Clarification reason: ${trace.normalized_output.reason}`);
  }
  if (trace.confirmation_decision) {
    lines.push(`Confirmation state: ${trace.confirmation_decision.state}`);
    lines.push(`Confirmation reason: ${trace.confirmation_decision.reason}`);
  }
  $("summaryPanel").textContent = `${lines.join("\n")}\n\nRaw trace JSON remains below for audit.`;
}

function eventTypeLabel(type) {
  const labels = {
    agentic: "Agentic verification",
    browser: "Browser action",
    confirmation: "Confirmation",
    clarification: "Clarification",
  };
  return labels[type] || "Trace event";
}

function addTimelineItem(label, text) {
  const item = document.createElement("li");
  item.textContent = `${label}: ${text}`;
  $("timeline").appendChild(item);
}

function renderTimeline(trace) {
  const timeline = $("timeline");
  timeline.innerHTML = "";
  if (trace.normalized_output?.kind === "clarification_request") {
    addTimelineItem(
      eventTypeLabel("clarification"),
      `${trace.normalized_output.reason} | ${trace.normalized_output.question}`,
    );
  }
  if (trace.confirmation_decision) {
    addTimelineItem(
      eventTypeLabel("confirmation"),
      `${trace.confirmation_decision.state} | ${trace.confirmation_decision.reason}`,
    );
  }
  for (const step of trace.agentic_steps || []) {
    const refs = (step.grounding_evidence_refs || []).join(", ");
    const screenshot = step.screenshot_ref ? ` | screenshot: ${step.screenshot_ref}` : "";
    const grounding = refs ? ` | grounding: ${refs}` : "";
    const verification = step.verification_decision
      ? ` | verification: ${step.verification_decision.reason}`
      : "";
    const recovery = step.recovery_decision
      ? ` | recovery: ${step.recovery_decision.kind} (${step.recovery_decision.reason})`
      : "";
    addTimelineItem(
      eventTypeLabel("agentic"),
      `step ${step.step_index}: ${step.observation_summary}` +
        `${step.selected_action ? ` | action: ${step.selected_action}` : ""}` +
        `${verification}${recovery}${screenshot}${grounding}`,
    );
  }
  for (const action of trace.browser_actions || []) {
    const refs = (action.grounding_evidence_refs || []).join(", ");
    const screenshot = action.screenshot_ref ? ` | screenshot: ${action.screenshot_ref}` : "";
    const grounding = refs ? ` | grounding: ${refs}` : "";
    addTimelineItem(
      eventTypeLabel("browser"),
      `${action.action_type}: ${action.description}${screenshot}${grounding}`,
    );
  }
}

function renderTrace(trace) {
  state.trace = trace;
  state.executionId = trace.execution_id;
  $("transcriptPanel").textContent = trace.transcript?.text || "";
  showJson("normalizedPanel", trace.normalized_output || {});
  showJson("tracePanel", trace);
  renderSummary(trace);
  renderTimeline(trace);
  const pending = trace.confirmation_decision?.state === "pending";
  $("confirmation").classList.toggle("hidden", !pending);
  $("confirmationReason").textContent = trace.confirmation_decision?.reason || "";
  const mode = trace.execution_mode || trace.execution_runtime?.execution_mode || "unknown";
  const reason = trace.stop_reason || trace.failure_reason || "";
  $("uploadStatus").textContent =
    `Execution mode: ${mode} | Status: ${trace.final_status || "unknown"}${reason ? ` | ${reason}` : ""}`;
  speakStatus(trace.status_voice);
}

function renderError(error) {
  $("uploadStatus").textContent = error.message || String(error);
}

function speakStatus(statusVoice) {
  if (!statusVoice?.enabled) return;
  if (!window.speechSynthesis) return;
  const text = statusVoice.text || "";
  if (!text) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "zh-CN";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
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

function fixtureById(fixtureId) {
  return state.fixtures.find((fixture) => fixture.id === fixtureId);
}

function renderFixtureOptions(fixtures) {
  const select = $("fixtureSelect");
  select.innerHTML = "";
  for (const fixture of fixtures) {
    const option = document.createElement("option");
    option.value = fixture.id;
    option.textContent = fixture.id;
    select.appendChild(option);
  }
}

function updateFixtureModeSupport() {
  const fixture = fixtureById($("fixtureSelect").value);
  const liveOption = [...$("executionMode").options].find((option) => option.value === "live_controlled");
  if (!fixture || !liveOption) return;
  const supportsLive = fixture.supported_execution_modes.includes("live_controlled");
  liveOption.disabled = !supportsLive;
  if (!supportsLive && $("executionMode").value === "live_controlled") {
    $("executionMode").value = "demo_preview";
  }
  $("fixtureModeHelp").textContent = supportsLive
    ? "live_controlled is available for this controlled local fixture."
    : "This fixture is preview-only unless selected for live-controlled execution.";
}

async function loadFixtures() {
  try {
    const response = await fetch("/api/fixtures");
    if (!response.ok) throw new Error(await response.text());
    const payload = await response.json();
    state.fixtures = payload.fixtures || [];
    renderFixtureOptions(state.fixtures);
    updateFixtureModeSupport();
  } catch (error) {
    state.fixtures = [...$("fixtureSelect").options].map((option) => ({
      id: option.value,
      supported_execution_modes: ["demo_preview"],
    }));
    updateFixtureModeSupport();
  }
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
  if (!response.ok) {
    $("uploadStatus").textContent = await response.text();
    return;
  }
  const commandInput = await response.json();
  state.audioId = commandInput.audio_id;
  $("audioRunButton").disabled = false;
  $("uploadStatus").textContent = `Audio accepted. audio_id: ${state.audioId}`;
});

$("transcriptRunButton").addEventListener("click", async () => {
  try {
    state.currentInputSource = "transcript-based execution";
    const transcript = $("transcriptInput").value.trim();
    const trace = await postJson("/api/executions", { transcript_text: transcript });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("fixtureRunButton").addEventListener("click", async () => {
  try {
    state.currentInputSource = "fixture-based execution";
    const fixtureId = $("fixtureSelect").value;
    const executionMode = $("executionMode").value;
    const trace = await postJson(`/api/fixtures/${fixtureId}/executions`, {
      execution_mode: executionMode,
    });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("audioRunButton").addEventListener("click", async () => {
  if (!state.audioId) {
    $("uploadStatus").textContent = "Upload or record audio before running audio execution.";
    return;
  }
  try {
    state.currentInputSource = "audio-based execution";
    const trace = await postJson("/api/executions", { audio_id: state.audioId });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("fixtureSelect").addEventListener("change", updateFixtureModeSupport);

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
    if (response.ok) {
      const commandInput = await response.json();
      state.audioId = commandInput.audio_id;
      $("audioRunButton").disabled = false;
      $("uploadStatus").textContent = `Recording accepted. audio_id: ${state.audioId}`;
    } else {
      $("uploadStatus").textContent = await response.text();
    }
    stream.getTracks().forEach((track) => track.stop());
  };
  state.recorder.start();
  $("uploadStatus").textContent = "Recording one command...";
});

loadFixtures();
