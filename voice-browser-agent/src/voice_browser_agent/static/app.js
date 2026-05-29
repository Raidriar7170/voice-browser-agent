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

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function setCards(id, cards) {
  $(id).innerHTML = cards
    .map(
      ([label, value, tone = ""]) =>
        `<div class="metric-card ${tone}"><span>${label}</span><strong>${value || "n/a"}</strong></div>`,
    )
    .join("");
}

function matrixRowForTrace(trace) {
  return trace.execution_runtime?.public_reliability_matrix_row || {};
}

function matrixOutcomeClass(outcome) {
  const classes = {
    completed: "matrix-outcome-completed",
    partial: "matrix-outcome-partial",
    stopped: "matrix-outcome-stopped",
    failed: "matrix-outcome-failed",
    blocked: "matrix-outcome-blocked",
  };
  return classes[outcome] || "warn";
}

function artifactImageSrc(trace, artifact) {
  if (!trace.execution_id || !artifact?.artifact_id) return "";
  return `/api/executions/${encodeURIComponent(trace.execution_id)}/visual-artifacts/${encodeURIComponent(
    artifact.artifact_id,
  )}`;
}

function renderVisualResult(trace) {
  const route = trace.route_decision || trace.execution_runtime?.route_decision || {};
  const runtime = trace.execution_runtime || {};
  const artifacts = runtime.public_visual_artifacts || [];
  const finalArtifact =
    runtime.public_final_visual_result ||
    [...artifacts].reverse().find((artifact) => artifact.is_final) ||
    artifacts.at(-1);
  const preview = $("visualResultPreview");
  const meta = $("visualResultMeta");
  const steps = $("visualStepTimeline");
  const isPublicRun = route.route_type === "public_readonly" || trace.execution_mode === "live_public_readonly";

  if (!isPublicRun) {
    preview.className = "visual-preview empty";
    preview.textContent = "No visual result captured";
    meta.innerHTML = "";
    steps.innerHTML = "";
    return;
  }

  if (!finalArtifact) {
    preview.className = "visual-preview empty";
    preview.textContent = "No visual result captured";
    const proof = runtime.public_observed_proof_summary || {};
    meta.innerHTML = Object.keys(proof).length
      ? `<span>proof: ${escapeHtml(Object.keys(proof).join(", "))}</span>`
      : `<span>state: ${escapeHtml(trace.final_status || "unknown")}</span>`;
    steps.innerHTML = "";
    return;
  }

  const outcome = runtime.public_completion_state || finalArtifact.completion_state;
  const statusClass = outcome === "completed" ? "good" : matrixOutcomeClass(outcome);
  preview.className = `visual-preview ${statusClass}`;
  preview.innerHTML = `<img alt="Public-readonly final visual result" src="${artifactImageSrc(
    trace,
    finalArtifact,
  )}" />`;
  meta.innerHTML = [
    ["Page", finalArtifact.page_title || route.public_target_label || "unknown"],
    ["Target", route.public_target_label || "public target"],
    ["Origin", finalArtifact.sanitized_origin || route.public_origin || "unknown"],
    ["Completion", finalArtifact.completion_state || runtime.public_completion_state || "unknown"],
    ["Privacy", finalArtifact.privacy_state || trace.evidence_privacy_state || "unknown"],
    ["Sanitizer", finalArtifact.sanitizer_status || trace.sanitizer_status || "unknown"],
  ]
    .map(([label, value]) => `<span><b>${escapeHtml(label)}</b>${escapeHtml(value)}</span>`)
    .join("");
  steps.innerHTML = artifacts
    .map(
      (artifact) => `
        <button class="visual-step" type="button" title="${escapeHtml(artifact.action_label)}">
          <img alt="${escapeHtml(artifact.action_label)}" src="${artifactImageSrc(trace, artifact)}" />
          <span>${escapeHtml(artifact.step_index || "")}</span>
        </button>
      `,
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
  const matrix = matrixRowForTrace(trace);
  const lines = [
    `Input source: ${inputSourceForTrace(trace)}`,
    `Route: ${route.route_type || "unknown"}`,
    `Execution mode: ${mode}`,
    `Evidence mode: ${route.evidence_mode || trace.execution_runtime?.evidence_mode || "unknown"}`,
    `Final status: ${trace.final_status || "unknown"}`,
  ];
  if (route.route_type === "public_readonly") {
    lines.push(`Public-readonly target: ${route.public_target_label || "unknown"}`);
    lines.push(`Public task: ${route.public_task_id || "unknown"} (${route.public_task_kind || "unknown"})`);
    lines.push(`Task category: ${route.public_task_category || matrix.task_category || "unknown"}`);
    lines.push(`Target class: ${route.public_target_class || matrix.target_class || "unknown"}`);
    lines.push(`Completion criteria: ${route.public_completion_criteria_id || "unknown"}`);
    lines.push(
      `Completion proof: ${(route.public_completion_criteria_summary || matrix.completion_criteria_summary || []).join(", ") || "unknown"}`,
    );
    lines.push(
      `Completion state: ${
        trace.execution_runtime?.public_completion_state || route.public_completion_state || "pending"
      }`,
    );
    lines.push(`Reliability matrix: ${matrix.outcome || "pending"}`);
    lines.push(`Visible result: ${matrix.visible_result_state || "not_captured"}`);
    lines.push(`Export state: ${matrix.export_state || route.public_evidence_export_state || "unknown"}`);
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
  const matrix = matrixRowForTrace(trace);
  const live = route.live_evidence_eligible ? "live evidence" : "not live evidence";
  const tone = route.live_evidence_eligible ? "good" : "warn";
  const limits = route.execution_limits || {};
  const outcome = matrix.outcome || trace.execution_runtime?.public_completion_state || route.public_completion_state;
  const criteriaSummary = route.public_completion_criteria_summary || matrix.completion_criteria_summary || [];
  setCards("routeCards", [
    ["Route", route.route_type || "unknown", tone],
    ["Target", route.public_target_label || route.controlled_fixture_id || "none"],
    ["Target class", route.public_target_class || matrix.target_class || "n/a"],
    ["Task category", route.public_task_category || matrix.task_category || "n/a"],
    ["Task", route.public_task_id || "n/a"],
    ["Task kind", route.public_task_kind || "n/a"],
    ["Mode", route.execution_mode || trace.execution_mode || "unknown"],
    ["Evidence", route.evidence_mode || trace.execution_runtime?.evidence_mode || "unknown"],
    ["Eligibility", live, tone],
    ["Matrix eligible", route.public_matrix_eligible ? "yes" : "no"],
    ["Allowlist", route.public_allowlist_id || "n/a"],
    ["Origin", route.public_origin || "n/a"],
    ["Criteria", route.public_completion_criteria_id || "n/a"],
    ["Criteria proof", criteriaSummary.length ? criteriaSummary.join(", ") : "n/a"],
    ["Outcome", outcome || "n/a", matrixOutcomeClass(outcome)],
    ["Completion", trace.execution_runtime?.public_completion_state || route.public_completion_state || "n/a", matrixOutcomeClass(outcome)],
    ["Privacy", route.evidence_privacy_state || trace.evidence_privacy_state || "n/a"],
    ["Sanitizer", route.sanitizer_status || trace.sanitizer_status || "n/a"],
    ["Export", matrix.export_state || route.public_evidence_export_state || "n/a"],
    ["Limits", limits.max_steps ? `${limits.max_steps} steps / ${limits.timeout_seconds}s` : "n/a"],
  ]);
  $("routeMessage").textContent = route.user_message || route.route_reason || "No route decision recorded.";
}

function renderEvidence(trace) {
  const route = trace.route_decision || {};
  const matrix = matrixRowForTrace(trace);
  const lastAction = (trace.browser_actions || []).at(-1) || {};
  const lastStep = (trace.agentic_steps || []).at(-1) || {};
  const browserState = lastAction.browser_state || lastStep.action_result?.browser_state || {};
  const refs = trace.grounding_evidence_refs || lastAction.grounding_evidence_refs || [];
  const completionState = trace.execution_runtime?.public_completion_state;
  const outcome = matrix.outcome || completionState;
  const observedProof = trace.execution_runtime?.public_observed_proof_summary || {};
  const unmetCriteria = trace.execution_runtime?.public_unmet_criteria || [];
  setCards("evidenceCards", [
    ["Status", trace.final_status || "unknown", outcome === "completed" ? "good" : matrixOutcomeClass(outcome)],
    ["Page", browserState.page_title || route.public_target_label || route.controlled_target_ref || "none"],
    ["Action", lastAction.action_type || lastStep.selected_action || "none"],
    ["Grounding", refs.length ? `${refs.length} refs` : "none"],
    ["Matrix outcome", outcome || "n/a", matrixOutcomeClass(outcome)],
    ["Public completion", completionState || "n/a", completionState === "completed" ? "good" : matrixOutcomeClass(outcome)],
    ["Observed proof", Object.keys(observedProof).length ? Object.keys(observedProof).join(", ") : "none"],
    ["Unmet criteria", unmetCriteria.length ? unmetCriteria.join(", ") : "none"],
    ["Visible result", matrix.visible_result_state || "n/a"],
    ["Export state", matrix.export_state || route.public_evidence_export_state || "n/a"],
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
  renderVisualResult(trace);
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

function compactField(value) {
  if (Array.isArray(value)) return value.length ? value.join(", ") : "none";
  if (value && typeof value === "object") {
    const entries = Object.entries(value).map(([key, item]) => `${key}: ${item}`);
    return entries.length ? entries.join(", ") : "none";
  }
  return value || "none";
}

function renderUsefulTaskPack(usefulTaskPack) {
  const usefulTaskPackRows = usefulTaskPack.rows || [];
  if (!usefulTaskPackRows.length) {
    return '<p class="hint">No useful task-pack rows are available.</p>';
  }
  return `
    <div class="task-pack-grid" aria-label="Useful task pack rows">
      ${usefulTaskPackRows
        .map(
          (row) => `
            <article class="task-pack-row ${matrixOutcomeClass(row.outcome)}">
              <header>
                <strong>${escapeHtml(row.target_label || row.task_id || "public task")}</strong>
                <span>${escapeHtml(row.task_category || "unknown")} · ${escapeHtml(row.outcome || "unknown")}</span>
              </header>
              <dl>
                <div><dt>Task</dt><dd>${escapeHtml(row.task_id || "unknown")}</dd></div>
                <div><dt>Kind</dt><dd>${escapeHtml(row.task_kind || "unknown")}</dd></div>
                <div><dt>Class</dt><dd>${escapeHtml(row.target_class || "unknown")}</dd></div>
                <div><dt>Criteria</dt><dd>${escapeHtml(compactField(row.completion_criteria_summary))}</dd></div>
                <div><dt>Proof</dt><dd>${escapeHtml(compactField(row.observed_proof_summary))}</dd></div>
                <div><dt>Unmet</dt><dd>${escapeHtml(compactField(row.unmet_criteria))}</dd></div>
                <div><dt>Reason</dt><dd>${escapeHtml(row.stop_or_failure_reason || "none")}</dd></div>
                <div><dt>Visible</dt><dd>${escapeHtml(row.visible_result_state || "unknown")}</dd></div>
                <div><dt>Privacy</dt><dd>${escapeHtml(row.evidence_privacy_state || "unknown")}</dd></div>
                <div><dt>Sanitizer</dt><dd>${escapeHtml(row.sanitizer_status || "unknown")}</dd></div>
                <div><dt>Export</dt><dd>${escapeHtml(row.export_state || "unknown")}</dd></div>
              </dl>
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

function renderTaskPackRun(taskPackRun) {
  if (!taskPackRun || taskPackRun.status !== "available") {
    return '<p class="hint">Latest task-pack run: no local/private runner manifest is available.</p>';
  }
  const counts = Object.entries(taskPackRun.outcome_counts || {})
    .map(([name, count]) => `${name}: ${count}`)
    .join(", ");
  const rows = taskPackRun.rows || [];
  return `
    <section aria-label="Latest task-pack run">
      <h3>Latest task-pack run</h3>
      <p class="hint">Run ${escapeHtml(taskPackRun.run_id || "unknown")} · ${escapeHtml(
        taskPackRun.runner_mode || "unknown",
      )} · ${escapeHtml(taskPackRun.selected_task_count || 0)} selected · ${escapeHtml(
        counts || "no outcome_counts",
      )} · ${escapeHtml(taskPackRun.privacy_state || "local_private")} · ${escapeHtml(
        taskPackRun.sanitizer_status || "unknown",
      )} · raw public runtime artifacts remain local/private.</p>
      <div class="task-pack-grid" aria-label="Latest task-pack run rows">
        ${rows
          .map(
            (row) => `
              <article class="task-pack-row ${matrixOutcomeClass(row.outcome)}">
                <header>
                  <strong>${escapeHtml(row.target_label || row.task_id || "public task")}</strong>
                  <span>${escapeHtml(row.runner_mode || taskPackRun.runner_mode || "runner")} · ${escapeHtml(
                    row.outcome || "unknown",
                  )}</span>
                </header>
                <dl>
                  <div><dt>Task</dt><dd>${escapeHtml(row.task_id || "unknown")}</dd></div>
                  <div><dt>Category</dt><dd>${escapeHtml(row.task_category || "unknown")}</dd></div>
                  <div><dt>Kind</dt><dd>${escapeHtml(row.task_kind || "unknown")}</dd></div>
                  <div><dt>Class</dt><dd>${escapeHtml(row.target_class || "unknown")}</dd></div>
                  <div><dt>Origin</dt><dd>${escapeHtml(row.sanitized_origin || "unknown")}</dd></div>
                  <div><dt>Criteria</dt><dd>${escapeHtml(compactField(row.completion_criteria_summary))}</dd></div>
                  <div><dt>Proof</dt><dd>${escapeHtml(compactField(row.observed_proof_summary))}</dd></div>
                  <div><dt>Unmet</dt><dd>${escapeHtml(compactField(row.unmet_criteria))}</dd></div>
                  <div><dt>Reason</dt><dd>${escapeHtml(row.stop_or_failure_reason || row.route_or_execution_reason || "none")}</dd></div>
                  <div><dt>Visible</dt><dd>${escapeHtml(row.visible_result_state || "unknown")}</dd></div>
                  <div><dt>Privacy</dt><dd>${escapeHtml(row.evidence_privacy_state || "unknown")}</dd></div>
                  <div><dt>Sanitizer</dt><dd>${escapeHtml(row.sanitizer_status || "unknown")}</dd></div>
                  <div><dt>Export</dt><dd>${escapeHtml(row.export_state || "unknown")}</dd></div>
                </dl>
              </article>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
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
  const usefulTaskPack = checks.public_readonly?.useful_task_pack || {};
  const latestTaskPackRun = checks.public_readonly?.latest_task_pack_run || {};
  const categoryCounts = usefulTaskPack.category_counts || {};
  const categorySummary = Object.entries(categoryCounts)
    .map(([name, count]) => `${name}: ${count}`)
    .join(", ");
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
    <p class="hint">Useful task pack: ${usefulTaskPack.status || "unknown"}; ${
      usefulTaskPack.task_count || 0
    } contracts; ${categorySummary || "no category_counts"}.</p>
    ${renderTaskPackRun(latestTaskPackRun)}
    ${renderUsefulTaskPack(usefulTaskPack)}
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
