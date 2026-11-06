#!/usr/bin/env bash
set -euo pipefail
cd /workspace/voiceiq-ai-feedback-intelligence
if [ ! -x /workspace/voiceiq-venv/bin/python ]; then
  python -m venv /workspace/voiceiq-venv
fi
/workspace/voiceiq-venv/bin/python -m pip install -r backend/requirements.txt
npm --prefix frontend ci --no-audit --no-fund
if [ ! -f artifacts/classifiers.joblib ]; then
  /workspace/voiceiq-venv/bin/python scripts/train.py
fi
if [ ! -f artifacts/voiceiq.db ]; then
  /workspace/voiceiq-venv/bin/python scripts/seed.py
fi
if [ ! -f artifacts/evaluation.json ]; then
  /workspace/voiceiq-venv/bin/python scripts/evaluate.py
fi
