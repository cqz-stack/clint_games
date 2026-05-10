#!/usr/bin/env bash
# Run The Periodic Wall. After CLT is fixed, plain "python3 periodic.py" works too.
set -euo pipefail
cd "$(dirname "$0")"

try_run() {
  local py="$1"
  if [[ ! -x "$py" ]]; then
    return 1
  fi
  if "$py" -c "import tkinter" 2>/dev/null; then
    exec "$py" periodic.py "$@"
  fi
  return 1
}

if try_run "/usr/bin/python3" "$@"; then exit 0; fi
if try_run "/opt/homebrew/bin/python3" "$@"; then exit 0; fi
if try_run "/usr/local/bin/python3" "$@"; then exit 0; fi

cat <<'EOF' >&2
No Python with tkinter found.

Your Command Line Tools are often the cause (missing xcrun). Fix:

  1) xcode-select --install
     → Finish the popup installer, then open a NEW terminal.

  2) If it still fails, remove the broken folder and reinstall:
       sudo rm -rf /Library/Developer/CommandLineTools
       xcode-select --install

Then from this directory:
       python3 periodic.py

Optional: if you use Homebrew Python without Tk:
       brew install python-tk@3.9
EOF
exit 1
