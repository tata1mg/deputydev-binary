#!/usr/bin/env bash
# build-windows-binary.sh
# Build a portable Windows [x64, arm64] Python app bundle with uv + python-build-standalone.
# Run this from Git Bash (no WSL or PowerShell please). Ensure uv, curl, tar, node are on PATH.
# use like --> ./build-windows-binary.sh that's all, ship the built binary tarball

set -Eeuo pipefail
IFS=$'\n\t'
umask 022

# ----------------------------
# Platform / Arch / Version
# ----------------------------
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS" in
  mingw*|msys*|cygwin*) OS="windows" ;;
  *) echo "✖ This script is Windows-only (Git Bash). Detected: $OS" >&2; exit 1 ;;
esac

ARCH="$(uname -m)"
case "$ARCH" in
  arm64|aarch64) ARCH="arm64" ;;
  x86_64|amd64)  ARCH="x64" ;;
  *) echo "✖ Unsupported architecture: $ARCH" >&2; exit 1 ;;
esac

VERSION="$(grep -E '^version\s*=' pyproject.toml | head -1 | cut -d'"' -f2)"
: "${PKG_TARBALL:=windows-${ARCH}-${VERSION}.tar.gz}"

# ----------------------------
# Config (override with env vars if you like)
# ----------------------------
: "${PY_DIR:=./binary_service}"        # where PBS Python is extracted
: "${STRIP_BINARIES:=0}"               # set to 1 to strip .pyd/.dll/rg to reduce size

# ----------------------------
# PBS URL + ripgrep per arch (Windows)
# ----------------------------
case "windows-$ARCH" in
  windows-x64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_windows_x64.exe"
    RIPGREP_DEST_REL="rg_windows_x64.exe"
    ;;
  windows-arm64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-aarch64-pc-windows-msvc-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_windows_arm64.exe"
    RIPGREP_DEST_REL="rg_windows_arm64.exe"
    ;;
  *)
    echo "✖ No PBS URL / ripgrep mapping for $OS-$ARCH" >&2; exit 1
    ;;
esac

# ----------------------------
# Helpers
# ----------------------------
msg()  { printf "\n\033[1;32m▶ %s\033[0m\n" "$*"; }
warn() { printf "\n\033[1;33m! %s\033[0m\n" "$*" >&2; }
err()  { printf "\n\033[1;31m✖ %s\033[0m\n" "$*" >&2; }
die()  { err "$@"; exit 1; }

TMPS=()
cleanup() {
  for f in "${TMPS[@]:-}"; do [[ -n "${f:-}" && -e "$f" ]] && rm -f "$f" || true; done
}
trap cleanup EXIT

# ----------------------------
# 0) Preconditions
# ----------------------------
command -v curl >/dev/null || die "curl is required."
command -v tar  >/dev/null || die "tar is required (Git Bash provides it)."
command -v uv   >/dev/null || die "uv is required (install: curl -LsSf https://astral.sh/uv/install.sh | sh)."

[[ -f "pyproject.toml" ]] || die "pyproject.toml not found in current directory."
[[ -f "$RIPGREP_SRC"    ]] || die "ripgrep binary not found at '$RIPGREP_SRC'."

# ----------------------------
# 1) Fetch PBS Python and extract to ./binary_service
# ----------------------------
msg "Downloading python-build-standalone for windows-$ARCH …"
TMP_TGZ="$(mktemp -t pbs-python.XXXXXX).tar.gz"; TMPS+=("$TMP_TGZ")

curl -fL --retry 3 --retry-connrefused --continue-at - --progress-bar \
  "$PBS_URL" -o "$TMP_TGZ"

msg "Extracting to $PY_DIR …"
rm -rf "$PY_DIR"
mkdir -p "$PY_DIR"
tar -xzf "$TMP_TGZ" -C "$PY_DIR" --strip-components 1

# ----------------------------
# 2) Locate interpreter (Windows PBS layout)
# ----------------------------
PYTHON="$PY_DIR/python.exe"
[[ -x "$PYTHON" ]] || die "Expected interpreter at $PYTHON not found."

msg "Found Python interpreter: $PYTHON"
msg "Embedded Python: $("$PYTHON" -V)"


[[ -x "$PYTHON" ]] || die "Expected interpreter under $PY_DIR not found."


msg "Embedded Python: $("$PYTHON" -V)"

# ----------------------------
# 3) Install project into embedded interpreter (uv pip)
# ----------------------------
msg "Installing project into embedded interpreter (with uv pip)…"
export PYTHONNOUSERSITE=1
env -u PYTHONPATH uv pip install --python "$PYTHON" . 

# ----------------------------
# 4) Trim tree-sitter to only requested bindings
# ----------------------------
KEEP_BINDINGS=( dockerfile make cmake python javascript typescript java c cpp go rust ruby html kotlin json tsx swift )

msg "Pruning tree-sitter bindings to only the requested set…"
SITE_PACKAGES="$("$PYTHON" - <<'PY'
import sysconfig, site
pure = sysconfig.get_paths().get("purelib")
print(pure if pure else site.getsitepackages()[0])
PY
)"
BINDINGS_DIR="$SITE_PACKAGES/tree_sitter_language_pack/bindings"

if [[ -d "$BINDINGS_DIR" ]]; then
  msg "Bindings dir: $BINDINGS_DIR"
  found_any="no"
  for k in "${KEEP_BINDINGS[@]}"; do
    if compgen -G "$BINDINGS_DIR/$k".{abi3.so,so,pyd,py} >/dev/null; then
      echo "  • requested & present: $k"
      found_any="yes"
    fi
  done
  [[ "$found_any" == "no" ]] && echo "  (none of the requested bindings are present)"

  shopt -s nullglob
  for path in "$BINDINGS_DIR"/*; do
    name="$(basename "$path")"
    if [[ "$name" == "__init__.py" ]]; then
      echo "  + kept    $name (package)"; continue
    fi
    base="$name"; base="${base%.abi3.so}"; base="${base%.so}"; base="${base%.pyd}"; base="${base%.py}"
    keep="no"
    for k in "${KEEP_BINDINGS[@]}"; do [[ "$base" == "$k" ]] && { keep="yes"; break; }; done
    if [[ "$keep" == "yes" ]]; then echo "  + kept    $name"; else rm -f "$path"; echo "  - removed $name"; fi
  done
  shopt -u nullglob
else
  msg "No tree_sitter_language_pack bindings directory found at $BINDINGS_DIR — skipping trim."
fi

# ----------------------------
# 5) Move ripgrep into binary_service/Scripts
# ----------------------------
msg "Moving ripgrep binary into portable tree…"
DEST_PATH="$PY_DIR/$RIPGREP_DEST_REL"
mkdir -p "$(dirname "$DEST_PATH")"
cp "$RIPGREP_SRC" "$DEST_PATH"
chmod +x "$DEST_PATH" || true
if command -v file >/dev/null 2>&1; then file "$DEST_PATH" || true; fi
echo "  -> placed at $DEST_PATH"

# ----------------------------
# Optional size trim (Windows)
# ----------------------------
if [[ "$STRIP_BINARIES" == "1" ]]; then
  msg "Stripping binaries to reduce size (optional)…"
  if command -v strip >/dev/null 2>&1; then
    # On Windows/PE: strip .pyd, .dll, and ripgrep exe (best-effort; may be limited depending on toolchain)
    find "$PY_DIR" -type f \( -name '*.pyd' -o -name '*.dll' -o -path "$DEST_PATH" \) \
      -exec strip --strip-unneeded {} + 2>/dev/null || true
  else
    warn "strip not found; skipping."
  fi
fi

# ----------------------------
# 6) Smoke test
# ----------------------------
msg "Smoke testing the embedded app…"
"$PYTHON" - <<'PY'
import sys, sysconfig
print("ok: using", sys.executable)
print("site-packages:", sysconfig.get_paths().get("purelib"))
PY

# ----------------------------
# 7) Package
# ----------------------------
msg "Creating tarball $PKG_TARBALL …"
# (COPYFILE_DISABLE is macOS-specific; harmless here but unnecessary)
tar -czf "$PKG_TARBALL" "$PY_DIR"

# ----------------------------
# 8) Checksum (use Windows path for Node if available)
# ----------------------------
if command -v node >/dev/null 2>&1; then
  msg "Computing checksum of $PY_DIR …"
  if command -v cygpath >/dev/null 2>&1; then
    WIN_PY_DIR="$(cygpath -w "$PY_DIR")"
    node hash-binary.js "$WIN_PY_DIR" || warn "Checksum failed"
  else
    node hash-binary.js "$PY_DIR" || warn "Checksum failed"
  fi
else
  warn "node not found, skipping checksum."
fi

msg "Done."
du -sh "$PY_DIR" "$PKG_TARBALL" 2>/dev/null || true
echo
echo "Portable artifact: $PKG_TARBALL"
