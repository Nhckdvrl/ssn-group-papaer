#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$project_dir/scripts/fetch_parent_data.sh"
/home/xiang/miniconda3/envs/verl-clean/bin/python "$project_dir/scripts/audit_parent.py"

