## ADDED Requirements

### Requirement: Provide static public evidence page
The project SHALL provide a sanitized static evidence page suitable for local review or static hosting.

#### Scenario: Reviewer opens public evidence page
- **WHEN** a reviewer opens the static public evidence page
- **THEN** it identifies the standalone Voice-to-Browser Agent scope, architecture, evidence modes, sanitized trace directories, release-pack workflow, seed-set workflow, validation commands, demo media contract, and limitations without requiring the Operator Console to run

#### Scenario: Public evidence page avoids raw runtime artifacts
- **WHEN** the page references generated release packs, demo media, traces, or datasets
- **THEN** it links to committed sanitized sources or documented local generation commands and does not require raw runtime outputs, raw recordings, private screenshots, credentials, private URLs, browser profiles, or remote host details

### Requirement: Include real-vision evidence in reviewer handoff
The reviewer evidence handoff SHALL surface real `browser-use-vision` controlled evidence separately from deterministic controlled evidence.

#### Scenario: Release pack includes real-vision evidence
- **WHEN** the release-pack workflow finds a sanitized real-vision controlled trace
- **THEN** the manifest and HTML index classify it with a distinct evidence mode and include provider metadata and privacy-scan status

#### Scenario: Required real-vision evidence is missing
- **WHEN** final public-evidence validation runs without the required sanitized real-vision controlled trace
- **THEN** it fails with a clear missing real-vision evidence reason

### Requirement: Provide short demo media contract
The project SHALL define a 60-90 second demo video or GIF contract for the bounded end-to-end workflow.

#### Scenario: Demo media plan is reviewed
- **WHEN** a reviewer opens the demo media plan
- **THEN** it describes exact steps for spoken or transcript input, normalization, safety gate behavior, visual execution, sanitized trace export, release-pack inspection, and seed-set inspection

#### Scenario: Demo media artifact is public-safe
- **WHEN** a demo video or GIF artifact is committed or referenced by the public evidence page
- **THEN** it contains no raw private recordings, credentials, private URLs, browser profile data, remote host details, or unsanitized runtime screenshots
