# Product case study
## Problem and users
Banking feedback is fragmented. Product managers need recurring pain points, support managers need urgent cases, and analysts need inspectable evidence. Manual categorization and disconnected spreadsheets delay investigation.
## Goals and MVP
Import, analyze, group, inspect and prioritize feedback with traceable evidence. Out of scope: production banking decisions, multilingual certification, CRM integrations and automated remediation.
## Stories and acceptance
As a support lead I upload feedback and see accepted, duplicate and rejected counts. As an analyst I filter and inspect persisted predictions and reason codes. As a PM I open recurring issues and recommendations with complaint references. Acceptance requires real HTTP-backed data, reproducible training, honest evaluation and no-key operation.
## Workflow and prioritization
Import → analysis job → filtered overview → complaint/cluster evidence → proposed improvement. Priority combines 45% normalized frequency, 35% severity, 20% recency; it is a transparent calculated ranking separate from AI wording.
## Success measures
Measure macro-F1, categorization coverage, human-rated evidence accuracy, generation latency, time to identify recurring issues and evidence-reference coverage. No business impact has yet been measured.
## Experiment
Randomize reviewers to manual CSV review or VoiceIQ with equal-size blinded batches. Measure completion time, issue recall against an adjudicated set, evidence accuracy and usefulness ratings. Predefine success thresholds and confidence intervals; never trade recall of critical cases for speed alone. This experiment is proposed, not performed.
## Limits and roadmap
Synthetic English data does not prove real-world accuracy. Next: consented representative evaluation, calibrated probabilities, human correction workflow, authenticated access, durable jobs and migrations for hosted use.
