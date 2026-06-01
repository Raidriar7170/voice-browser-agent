# Voice-to-Browser Agent

[![Front Door](https://github.com/Raidriar7170/voice-browser-agent/actions/workflows/front-door.yml/badge.svg)](https://github.com/Raidriar7170/voice-browser-agent/actions/workflows/front-door.yml)
[![Reliability](https://github.com/Raidriar7170/voice-browser-agent/actions/workflows/reliability.yml/badge.svg)](https://github.com/Raidriar7170/voice-browser-agent/actions/workflows/reliability.yml)
[![Release](https://img.shields.io/github/v/release/Raidriar7170/voice-browser-agent?label=release)](https://github.com/Raidriar7170/voice-browser-agent/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![Status](https://img.shields.io/badge/status-final%20local%20MVP-green.svg)
![Scope](https://img.shields.io/badge/scope-bounded%20browser%20execution-orange.svg)

**A bounded Chinese-first Voice-to-Browser Agent that turns one spoken command into
a safe, inspectable browser task execution trace.**

一个面向中文 spoken command 的有界浏览器 Agent：它把一次语音/转写命令转换成结构化
浏览器任务，经过确定性安全门、任务路由和视觉验证后执行，并输出可复核的 sanitized
trace，而不是只给出“成功了”的口头结果。

---

## TL;DR

This repository is a final local MVP and evidence pack for a Voice-to-Browser
Agent. It demonstrates a command-first operator console, speech-to-task
normalization, bounded browser execution, visual grounding through
`browser-use-vision`, visual verification loop evidence, public-readonly task
contracts, and local adaptation-readiness evaluation.

这个项目的重点不是做一个泛化语音助手，也不是宣称公网自动化或模型 SOTA。它更像一个
可审计的 agent reliability demo：每一步都能回到 schema、route decision、safety gate、
visual verification result 和 sanitized artifact 核验。

Latest closeout state:

| Item | Status |
|---|---|
| OpenSpec lifecycle | Closeout archived; reliability gate archived on 2026-06-01 |
| Operator Console UI | Operations-dashboard polish archived on 2026-06-01 |
| Front Door CI | `.github/workflows/front-door.yml` checks the public entry surface |
| Reliability CI | `.github/workflows/reliability.yml` runs OpenSpec strict validation and a CI-safe pytest subset |
| Local tests | Re-run `uv run pytest` for the full local project suite |
| OpenSpec validation | Re-run `OPENSPEC_TELEMETRY=0 openspec validate --all --strict` |
| Public scope | Local bounded MVP and reviewer evidence pack |
| Explicitly not claimed | Fine-tuning, checkpoint release, ASR/TTS benchmark, public leaderboard, production autonomy |

## Navigation / 导航

- [Project Positioning / 项目定位](#project-positioning--项目定位)
- [Architecture / 系统架构](#architecture--系统架构)
- [What Is Implemented / 已实现内容](#what-is-implemented--已实现内容)
- [Operator Console / 操作台体验](#operator-console--操作台体验)
- [Evidence Boundary / 证据边界](#evidence-boundary--证据边界)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [Minimal Reviewer Path / 最小复核路径](#minimal-reviewer-path--最小复核路径)
- [CI And Local Evidence Boundary / CI 与本地证据边界](#ci-and-local-evidence-boundary--ci-与本地证据边界)
- [Evidence Map / 证据地图](#evidence-map--证据地图)
- [Validation / 验证](#validation--验证)

## Project Positioning / 项目定位

Most voice-agent demos optimize for a polished interaction. This project
optimizes for bounded execution and reviewability: what command was heard, how it
was normalized, why it was allowed or stopped, what browser state was observed,
and which sanitized artifacts support the result.

大多数语音 Agent demo 关注“它能不能聊起来”。这个项目关注的是更工程化的问题：语音命令
如何变成一个受约束的 browser task，哪些任务必须停下确认，视觉状态是否真的被验证，
以及 reviewer 能否从 artifact 反查每个结论。

| This project is | This project is not |
|---|---|
| A local Chinese-first Voice-to-Browser Agent MVP | A general-purpose voice assistant |
| A bounded browser execution and trace evidence system | Unrestricted public-web autonomy |
| A reviewer-friendly demo with sanitized artifacts | A production browser automation product |
| A visual grounding integration that reuses `browser-use-vision` | A fork or voice extension of `browser-use-vision` |
| A speech-to-task dataset and evaluation preparation surface | A completed fine-tuning project or checkpoint release |

## Architecture / 系统架构

```text
spoken command / fixture transcript / reviewed ASR transcript
        |
        v
  spoken-command ingestion
        |
        v
  normalizer
  rule / mock LLM / optional private provider
        |
        v
  deterministic validator + confirmation gates
        |
        v
  task router
  demo_preview / live_controlled / live_public_readonly
        |
        v
  browser executor + browser-use-vision grounding
        |
        v
  visual verification loop
        |
        v
  sanitized execution trace + release-pack evidence
```

Key design choices:

- **Chinese-first commands:** fixtures and prompts support Chinese instructions
  with expected English code-switching for product names, URLs, UI labels, and
  technical terms.
- **Bounded execution:** the system routes only known task categories and stops
  for ambiguous, destructive, private, or unsupported commands.
- **Visual grounding:** browser perception is delegated to `browser-use-vision`
  instead of duplicating that project inside this repository.
- **Trace-first evidence:** execution outputs record route, safety decision,
  visual verification outcome, proof references, and sanitizer status.
- **Private-by-default runtime:** raw recordings, screenshots, browser state,
  provider responses, credentials, checkpoints, and local runtime paths are not
  public evidence.

## What Is Implemented / 已实现内容

| Surface | Implemented evidence |
|---|---|
| Operator Console | Local FastAPI console for transcript input, audio review, route summary, visual result, and raw trace inspection |
| Spoken Command Normalization | Rule normalizer plus mock/provider structured-output modes behind schema validation |
| Safety Gates | Clarification, confirmation, cancellation, route policy, and destructive/private-task stops |
| Controlled Browser Tasks | Icon search, color swatch, SVG/dashboard, settings, CRM-like and GitHub-like local demo pages |
| Public-Readonly Lane | Opt-in allowlisted public documentation/reference/repository-read contracts with private local traces |
| Visual Verification | Deterministic controlled-task verification with pass/fail/uncertain outcomes and recovery/stop decisions |
| Evidence Pack | Sanitized fixtures, public evidence HTML, release-pack builder, and machine-readable manifests |
| Speech-to-Task Preparation | Trace-derived seed examples, evaluation splits, and candidate-output evaluation harness |

## Operator Console / 操作台体验

The current local Operator Console is organized as an operations dashboard rather
than a raw debug page: command input and reviewed audio stay first, readiness and
route decisions are visible near the action, evidence/result panels summarize the
run before raw trace JSON, and advanced replay remains secondary.

![Operator Console desktop screenshot](docs/human-briefs/assets/2026-06-01-polish-operator-console-ui-after-desktop.png)

Use it from top to bottom:

1. Start the local FastAPI app and open the console.
2. Check real-use readiness before uploaded or recorded audio.
3. Run a typed command, or upload/record audio and review the ASR transcript.
4. Inspect route decision, visible result, execution evidence, timeline, and
   export/privacy state before opening raw trace JSON.

The UI polish is a presentation and reviewability improvement. It does not widen
the execution policy: public-readonly traces, task-pack rows, visual artifacts,
and exports remain local/private unless sanitizer approval is explicit. The
archived change brief is
[`docs/human-briefs/2026-06-01-polish-operator-console-ui.html`](docs/human-briefs/2026-06-01-polish-operator-console-ui.html).

## Evidence Boundary / 证据边界

The project intentionally separates local, inspectable MVP evidence from broader
claims.

当前 evidence 支持这些结论：

- A spoken or reviewed transcript can become a structured browser task request.
- The request is checked by deterministic schema, validator, confirmation, and
  route gates before execution.
- Controlled local visual tasks produce sanitized execution traces.
- Public-readonly tasks are constrained by explicit task contracts and remain
  local/private unless sanitized.
- Speech-to-task adaptation data and evaluation surfaces exist for future model
  work.

当前 evidence 不支持这些结论：

- It is not a production voice assistant.
- It is not a broad public-web automation agent.
- It is not an ASR, TTS, or multimodal model benchmark.
- It does not publish fine-tuned checkpoints or claim fine-tuning gains.
- It does not claim leaderboard-style model superiority.

## Quick Start / 快速开始

The runnable Python package lives in
[`voice-browser-agent/`](voice-browser-agent/). Use Python 3.11+ and `uv`.

```bash
cd voice-browser-agent
uv sync --extra dev
uv run uvicorn voice_browser_agent.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

You can paste a fixture transcript, upload a supported audio file, or use the
reviewed ASR flow. Fixture manifests live under
[`voice-browser-agent/fixtures/audio/`](voice-browser-agent/fixtures/audio/).

Before real audio or browser execution, run the local readiness check:

```bash
cd voice-browser-agent
uv run python scripts/preflight_real_use.py
```

For the full runtime details, environment variables, public-readonly setup, and
evidence-pack commands, see
[`voice-browser-agent/README.md`](voice-browser-agent/README.md).

## Minimal Reviewer Path / 最小复核路径

For a quick external review, use the deterministic evidence path first. It does
not require real audio, provider credentials, live public browsing, model
training, or a full `browser-use-vision` live runtime.

```bash
git clone https://github.com/Raidriar7170/voice-browser-agent.git
cd voice-browser-agent/voice-browser-agent
uv sync --extra dev
uv run python scripts/run_public_readonly_task_pack.py --all --mode deterministic
uv run python scripts/build_demo_evidence_pack.py
```

Then inspect `runtime/demo-evidence-release-pack/index.html` or
`runtime/demo-evidence-release-pack/manifest.json`. These generated `runtime/`
outputs stay local/private; committed public evidence remains the sanitized
fixtures, docs, OpenSpec archives, and Human Brief links in this README.

## CI And Local Evidence Boundary / CI 与本地证据边界

GitHub validation is intentionally split:

- `.github/workflows/front-door.yml` keeps the public README, license, JSON, and
  Python compile checks fast.
- `.github/workflows/reliability.yml` runs OpenSpec strict validation plus a
  CI-safe pytest subset for docs, schemas, deterministic evidence builders,
  privacy guards, and release-pack contracts.

The CI-safe pytest subset is not live public browsing, not recorded-audio, not real-provider inference, and not model training. Full local validation can still
run `uv run pytest` from `voice-browser-agent/` when the editable
`browser-use-vision` sibling, Playwright/browser runtime, and local/private
artifacts are available.

Generate the local reliability snapshot with:

```bash
cd voice-browser-agent
uv run python scripts/build_reliability_snapshot.py
```

It writes `runtime/reliability-snapshot/manifest.json`, an ignored
local/private summary of committed sanitized evidence and optional runtime
manifests. It is not committed raw evidence.

## Evidence Map / 证据地图

| Artifact | Purpose |
|---|---|
| [`voice-browser-agent/docs/interview-project-overview.html`](voice-browser-agent/docs/interview-project-overview.html) | Interview-facing project overview |
| [`voice-browser-agent/docs/public-evidence/index.html`](voice-browser-agent/docs/public-evidence/index.html) | Browser-readable public evidence page |
| [`voice-browser-agent/docs/demo/demo-task-suite.md`](voice-browser-agent/docs/demo/demo-task-suite.md) | Controlled demo task suite |
| [`voice-browser-agent/docs/demo/useful-scenarios.md`](voice-browser-agent/docs/demo/useful-scenarios.md) | Useful local/public-readonly scenario framing |
| [`voice-browser-agent/docs/demo/ablations.md`](voice-browser-agent/docs/demo/ablations.md) | Module-value ablation notes without leaderboard claims |
| [`voice-browser-agent/docs/demo/video-plan.md`](voice-browser-agent/docs/demo/video-plan.md) | Demo recording plan and evidence checklist |
| [`voice-browser-agent/docs/demo/speech-to-task-dataset.md`](voice-browser-agent/docs/demo/speech-to-task-dataset.md) | Speech-to-task dataset and correction overlay format |
| [`voice-browser-agent/fixtures/traces/sanitized/`](voice-browser-agent/fixtures/traces/sanitized/) | Demo-preview sanitized traces |
| [`voice-browser-agent/fixtures/traces/live-sanitized/`](voice-browser-agent/fixtures/traces/live-sanitized/) | Live controlled sanitized traces |
| [`voice-browser-agent/fixtures/traces/agentic-sanitized/`](voice-browser-agent/fixtures/traces/agentic-sanitized/) | Agentic controlled traces with visual verification |
| [`voice-browser-agent/fixtures/traces/real-vision-sanitized/`](voice-browser-agent/fixtures/traces/real-vision-sanitized/) | Real `browser-use-vision` controlled trace metadata |
| [`voice-browser-agent/fixtures/traces/real-voice-sanitized/`](voice-browser-agent/fixtures/traces/real-voice-sanitized/) | Real voice controlled smoke trace |
| [`voice-browser-agent/fixtures/traces/real-use-sanitized/`](voice-browser-agent/fixtures/traces/real-use-sanitized/) | Failure and operator-decision traces |
| [`docs/human-briefs/2026-06-01-polish-operator-console-ui.html`](docs/human-briefs/2026-06-01-polish-operator-console-ui.html) | Human review brief and screenshots for the polished Operator Console |
| [`openspec/changes/archive/2026-05-30-final-project-completion-audit/`](openspec/changes/archive/2026-05-30-final-project-completion-audit/) | Final project completion audit archive |
| [`openspec/changes/archive/2026-06-01-polish-operator-console-ui/`](openspec/changes/archive/2026-06-01-polish-operator-console-ui/) | Archived OpenSpec change for the Operator Console UI polish |

Build a local reviewer release pack from committed evidence:

```bash
cd voice-browser-agent
uv run python scripts/build_demo_evidence_pack.py
```

Optional local comparison and adaptation-readiness summaries can be included when
their manifests exist:

```bash
cd voice-browser-agent
uv run python scripts/build_normalizer_comparison.py --seed-set
uv run python scripts/build_speech_to_task_dataset.py --seed-set --evaluation-splits
uv run python scripts/build_speech_to_task_eval.py \
  --dataset-manifest runtime/speech-to-task-adaptation-dataset/manifest.json
uv run python scripts/build_demo_evidence_pack.py \
  --normalizer-comparison-path runtime/normalizer-comparison/manifest.json \
  --adaptation-eval-path runtime/speech-to-task-adaptation-eval/manifest.json
```

Generated `runtime/` outputs stay local and are not committed as public raw
evidence.

## Project Layout / 项目结构

```text
.
├── CONTEXT.md                         # domain language and coverage matrix
├── docs/adr/                          # architectural decisions
├── openspec/                          # specs and archived change lifecycle
└── voice-browser-agent/
    ├── src/voice_browser_agent/        # FastAPI app, schemas, routing, execution, safety
    ├── tests/                          # pytest suite
    ├── scripts/                        # evidence, dataset, eval, and readiness commands
    ├── demo/pages/                     # controlled local browser task pages
    ├── fixtures/                       # audio manifests, task packs, sanitized traces
    └── docs/                           # demo docs, public evidence, interview overview
```

## Validation / 验证

From the repository root:

```bash
OPENSPEC_TELEMETRY=0 openspec validate --all --strict
cd voice-browser-agent
uv run python scripts/build_reliability_snapshot.py
uv run pytest
git diff --check
```

The final completion audit also records this closeout state in
[`openspec/changes/archive/2026-05-30-final-project-completion-audit/`](openspec/changes/archive/2026-05-30-final-project-completion-audit/).
