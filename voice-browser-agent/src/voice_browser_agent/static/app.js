const state = {
  executionId: null,
  trace: null,
  recorder: null,
  chunks: [],
  audioId: null,
  reviewedTranscript: null,
  fixtures: [],
  currentInputSource: null,
};

const $ = (id) => document.getElementById(id);

function showJson(id, value) {
  $(id).textContent = JSON.stringify(value, null, 2);
}

function setCards(id, cards) {
  $(id).innerHTML = cards
    .map(
      ([label, value, tone = ""]) =>
        `<div class="metric-card ${tone}"><span>${label}</span><strong>${value || "n/a"}</strong></div>`,
    )
    .join("");
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
  const route = trace.route_decision || trace.execution_runtime?.route_decision || {};
  const lines = [
    `Input source: ${inputSourceForTrace(trace)}`,
    `Route: ${route.route_type || "unknown"}`,
    `Execution mode: ${mode}`,
    `Evidence mode: ${route.evidence_mode || trace.execution_runtime?.evidence_mode || "unknown"}`,
    `Final status: ${trace.final_status || "unknown"}`,
  ];
  if (route.route_type === "public_readonly") {
    lines.push(`Public-readonly target: ${route.public_target_label || "unknown"}`);
    lines.push(`Private trace state: ${route.evidence_privacy_state || trace.evidence_privacy_state || "unknown"}`);
    lines.push(`Sanitizer status: ${route.sanitizer_status || trace.sanitizer_status || "unknown"}`);
  }
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

function renderRoute(trace) {
  const route = trace.route_decision || trace.execution_runtime?.route_decision || {};
  const live = route.live_evidence_eligible ? "live evidence" : "not live evidence";
  const tone = route.live_evidence_eligible ? "good" : "warn";
  const limits = route.execution_limits || {};
  setCards("routeCards", [
    ["Route", route.route_type || "unknown", tone],
    ["Target", route.public_target_label || route.controlled_fixture_id || "none"],
    ["Mode", route.execution_mode || trace.execution_mode || "unknown"],
    ["Evidence", route.evidence_mode || trace.execution_runtime?.evidence_mode || "unknown"],
    ["Eligibility", live, tone],
    ["Allowlist", route.public_allowlist_id || "n/a"],
    ["Origin", route.public_origin || "n/a"],
    ["Privacy", route.evidence_privacy_state || trace.evidence_privacy_state || "n/a"],
    ["Sanitizer", route.sanitizer_status || trace.sanitizer_status || "n/a"],
    ["Limits", limits.max_steps ? `${limits.max_steps} steps / ${limits.timeout_seconds}s` : "n/a"],
  ]);
  $("routeMessage").textContent = route.user_message || route.route_reason || "No route decision recorded.";
}

function renderEvidence(trace) {
  const route = trace.route_decision || {};
  const lastAction = (trace.browser_actions || []).at(-1) || {};
  const lastStep = (trace.agentic_steps || []).at(-1) || {};
  const browserState = lastAction.browser_state || lastStep.action_result?.browser_state || {};
  const refs = trace.grounding_evidence_refs || lastAction.grounding_evidence_refs || [];
  setCards("evidenceCards", [
    ["Status", trace.final_status || "unknown", trace.final_status === "succeeded" ? "good" : "warn"],
    ["Page", browserState.page_title || route.public_target_label || route.controlled_target_ref || "none"],
    ["Action", lastAction.action_type || lastStep.selected_action || "none"],
    ["Grounding", refs.length ? `${refs.length} refs` : "none"],
    ["Trace privacy", trace.evidence_privacy_state || route.evidence_privacy_state || "n/a"],
    ["Sanitizer", trace.sanitizer_status || route.sanitizer_status || "n/a"],
  ]);
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
  renderRoute(trace);
  renderEvidence(trace);
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

function renderReadiness(report) {
  const checks = report.checks || {};
  const primary_asr = checks.primary_asr || {};
  const fallback_asr = checks.fallback_asr || {};
  const items = [
    ["primary_asr", primary_asr],
    ["fallback_asr", fallback_asr],
    ["browser_automation", checks.browser_automation || {}],
    ["real_vision_grounding", checks.real_vision_grounding || {}],
    ["runtime_privacy", checks.runtime_privacy || {}],
    ["public_readonly", checks.public_readonly || {}],
  ];
  const actions = report.recommended_actions || [];
  const unavailable =
    primary_asr.status !== "configured" && fallback_asr.status !== "ready"
      ? '<p class="hint">ASR unavailable: configure a primary ASR endpoint or install the local fallback.</p>'
      : "";
  $("readinessPanel").innerHTML = `
    <h2>Real-Use Readiness</h2>
    <div class="readiness-grid">
      ${items
        .map(
          ([name, check]) =>
            `<div class="readiness-item"><strong>${name}</strong><span>${check.status || "unknown"}</span></div>`,
        )
        .join("")}
    </div>
    <p class="hint">Public-readonly: ${
      checks.public_readonly?.enabled ? "enabled for allowlisted read-only targets" : "disabled by default"
    }.</p>
    ${unavailable}
    <p class="hint">${actions.join(" ")}</p>
  `;
}

async function loadReadiness() {
  try {
    const response = await fetch("/api/readiness");
    if (!response.ok) throw new Error(await response.text());
    renderReadiness(await response.json());
  } catch (error) {
    $("readinessPanel").innerHTML = `
      <h2>Real-Use Readiness</h2>
      <p class="hint">ASR unavailable: run the preflight command before real audio execution.</p>
    `;
  }
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

function resetAudioReview() {
  state.reviewedTranscript = null;
  $("audioReviewButton").disabled = !state.audioId;
  $("audioPreviewButton").disabled = true;
  $("audioRunButton").disabled = true;
  $("reviewedTranscriptInput").value = "";
  $("asrReviewStatus").textContent = "Review ASR output before running reviewed audio.";
}

async function runCommand() {
  try {
    state.currentInputSource = "transcript-based execution";
    const transcript = $("transcriptInput").value.trim();
    const trace = await postJson("/api/executions", { transcript_text: transcript });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
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
  resetAudioReview();
  $("uploadStatus").textContent = `Audio accepted. audio_id: ${state.audioId}`;
});

$("primaryRunButton").addEventListener("click", runCommand);
$("transcriptRunButton").addEventListener("click", runCommand);

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
    const reviewed = $("reviewedTranscriptInput").value.trim() || state.reviewedTranscript || "";
    if (!reviewed) {
      $("uploadStatus").textContent = "Review ASR transcript before running reviewed audio.";
      return;
    }
    const trace = await postJson("/api/executions", {
      audio_id: state.audioId,
      reviewed_transcript_text: reviewed,
    });
    renderTrace(trace);
  } catch (error) {
    renderError(error);
  }
});

$("audioReviewButton").addEventListener("click", async () => {
  if (!state.audioId) {
    $("uploadStatus").textContent = "Upload or record audio before ASR review.";
    return;
  }
  try {
    const transcript = await postJson(`/api/audio/${state.audioId}/transcript`, {});
    state.reviewedTranscript = transcript.text || "";
    $("reviewedTranscriptInput").value = state.reviewedTranscript;
    $("audioPreviewButton").disabled = false;
    $("audioRunButton").disabled = false;
    const metadata = transcript.metadata || {};
    $("asrReviewStatus").textContent =
      `ASR: ${metadata.adapter_name || "unknown"} | confidence: ${metadata.confidence ?? "unknown"}`;
  } catch (error) {
    $("asrReviewStatus").textContent = `ASR unavailable: ${error.message || String(error)}`;
    renderError(error);
  }
});

$("audioPreviewButton").addEventListener("click", async () => {
  if (!state.audioId) return;
  try {
    state.currentInputSource = "audio-based execution";
    const reviewed = $("reviewedTranscriptInput").value.trim() || state.reviewedTranscript || "";
    const trace = await postJson("/api/normalize", {
      audio_id: state.audioId,
      reviewed_transcript_text: reviewed,
    });
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
    const exported = await response.json();
    showJson("tracePanel", exported);
    if (exported.route_decision?.route_type === "public_readonly") {
      const publicSafe =
        exported.evidence_privacy_state === "public_safe" && exported.sanitizer_status === "passed";
      if (publicSafe) {
        $("uploadStatus").textContent = "Exported public-readonly trace is public-safe.";
      } else if (exported.sanitizer_status === "failed") {
        $("uploadStatus").textContent = "Exported public-readonly trace failed sanitizer checks.";
      } else {
        $("uploadStatus").textContent = "Exported public-readonly trace remains local/private.";
      }
    }
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
      resetAudioReview();
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
loadReadiness();
