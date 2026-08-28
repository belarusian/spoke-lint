#!/bin/bash
# mission-compiler launch script (minimal repro of launch-gate launch-setup.sh)
set -uo pipefail
export FIVE_MODEL="fast-qwen"
export FIVE_BASE_URL="http://192.168.1.157:8080/v1"
REG_DIR="$HOME/.four/launches"
mkdir -p "$REG_DIR"
trap 'rm -f "$REG_DIR/launch-gate.json"' EXIT
INNER=$(cat <<'INNER_EOF'
python3 /home/sasha/Research/four/examples/spokes/project-setup.py --goal "Mission: Build launch-gate: a deterministic, stdlib-only Python CLI (package launch_gate, entrypoint python3 -m launch_gate) that gates a four pipeline launch at the launch moment. exit codes 0=all-GO / 1=any-NO-GO / 2=usage-error, pytest + ruff + mypy gate." --name launch-gate --project-dir /home/sasha/AI/launch-gate/proj --ai-dir /home/sasha/AI/launch-gate/ai --cycles 12 --repo belarusian/launch-gate --seed /home/sasha/AI/launch-gate/seed
INNER_EOF
)
echo "========== launch-gate launch =========="
