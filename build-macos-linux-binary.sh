#!/usr/bin/env bash
# build-macos-linux-binary.sh
# Build a portable macOS [arm64,x64] / linux [arm64,x64] Python app bundle with uv + python-build-standalone.
# Ensure uv, curl, tar, node are on PATH.
# use like --> ./build-macos-linux-binary.sh that's all, ship the built binary tarball

set -Eeuo pipefail
IFS=$'\n\t'
umask 022


# ----------------------------
# Platform / Arch / Version
# ----------------------------
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS" in
  darwin)  OS="macos" ;;
  linux)   OS="linux" ;;
esac

ARCH="$(uname -m)"
case "$ARCH" in
  arm64|aarch64) ARCH="arm64" ;;
  x86_64|amd64)  ARCH="x64" ;;
esac

VERSION="$(grep -E '^version\s*=' pyproject.toml | head -1 | cut -d'"' -f2)"

: "${PKG_TARBALL:=${OS}-${ARCH}-${VERSION}.tar.gz}"



# ----------------------------
# Config (override with env vars if you like)
# ----------------------------
: "${PY_DIR:=./binary_service}"   # where PBS Python is extracted
: "${STRIP_BINARIES:=0}"           # set to 1 to strip .so/rg to reduce size

# ----------------------------
# PBS + Ripgrep by platform/arch
# ----------------------------
case "$OS-$ARCH" in
  macos-arm64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-aarch64-apple-darwin-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_darwin_arm"
    RIPGREP_DEST_REL="bin/rg_darwin_arm"
    ;;
  macos-x64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-x86_64-apple-darwin-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_darwin_x64"
    RIPGREP_DEST_REL="bin/rg_darwin_x64"
    ;;
  linux-x64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-x86_64_v4-unknown-linux-gnu-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_linux_x64"
    RIPGREP_DEST_REL="bin/rg_linux_x64"
    ;;
  linux-arm64)
    PBS_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20250902/cpython-3.11.13+20250902-aarch64-unknown-linux-gnu-install_only_stripped.tar.gz"
    RIPGREP_SRC="ripgrep/rg_linux_arm64"
    RIPGREP_DEST_REL="bin/rg_linux_arm64"
    ;;
  *)
    die "No PBS URL / ripgrep binary defined for $OS-$ARCH"
    ;;
esac


# Tree-sitter bindings to keep
KEEP_BINDINGS=(
  dockerfile make cmake python javascript typescript java c cpp
  go rust ruby html kotlin json tsx swift
)

# ----------------------------
# Helpers
# ----------------------------
msg() { printf "\n\033[1;32m▶ %s\033[0m\n" "$*"; }
warn() { printf "\n\033[1;33m! %s\033[0m\n" "$*" >&2; }
err() { printf "\n\033[1;31m✖ %s\033[0m\n" "$*" >&2; }
die() { err "$@"; exit 1; }

TMPS=()
cleanup() {
  # remove any tmp files we created
  for f in "${TMPS[@]:-}"; do [[ -n "${f:-}" && -e "$f" ]] && rm -f "$f" || true; done
}
trap cleanup EXIT

# ----------------------------
# 0) Preconditions
# ----------------------------
case "$OS" in
  macos|linux) : ;;  # supported
  *) die "Unsupported OS: $OS" ;;
esac

case "$ARCH" in
  arm64|x64) : ;;  # supported
  *) die "Unsupported architecture: $ARCH" ;;
esac


command -v curl >/dev/null || die "curl is required."
command -v tar  >/dev/null || die "tar is required."
command -v uv   >/dev/null || die "uv is required (install: curl -LsSf https://astral.sh/uv/install.sh | sh)."

[[ -f "pyproject.toml" ]] || die "pyproject.toml not found in current directory."
[[ -f "$RIPGREP_SRC" ]] || die "ripgrep binary not found at '$RIPGREP_SRC'."

# ----------------------------
# 1) Fetch PBS Python and extract to ./binary_service
# ----------------------------
msg "Downloading python-build-standalone for $OS-$ARCH …"
TMP_TGZ="$(mktemp -t pbs-python.XXXXXX).tar.gz"; TMPS+=("$TMP_TGZ")

# retry a couple times; allow resume
curl -fL --retry 3 --retry-connrefused --continue-at - --progress-bar \
  "$PBS_URL" -o "$TMP_TGZ"


msg "Extracting to $PY_DIR …"
rm -rf "$PY_DIR"
mkdir -p "$PY_DIR"
tar -xzf "$TMP_TGZ" -C "$PY_DIR" --strip-components 1

# ----------------------------
# 2) Verify interpreter
# ----------------------------
PYTHON="$PY_DIR/bin/python3"
[[ -x "$PYTHON" ]] || die "Expected interpreter at $PYTHON not found."
msg "Embedded Python: $("$PYTHON" -V)"

# ----------------------------
# 3) Sync deps/app into PBS Python with uv
# ----------------------------
msg "Installing project into embedded interpreter (with uv pip)…"
export PYTHONNOUSERSITE=1
# If user had PYTHONPATH set, ignore it for a hermetic build
env -u PYTHONPATH uv pip install --python "$PYTHON" .

# ----------------------------
# 4) Trim tree-sitter to only requested bindings
# ----------------------------
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

  # Show which requested bindings are present (check common suffixes)
  found_any="no"
  for k in "${KEEP_BINDINGS[@]}"; do
    if compgen -G "$BINDINGS_DIR/$k".{abi3.so,so,pyd,py} > /dev/null; then
      echo "  • requested & present: $k"
      found_any="yes"
    fi
  done
  [[ "$found_any" == "no" ]] && echo "  (none of the requested bindings are present)"

  shopt -s nullglob
  for path in "$BINDINGS_DIR"/*; do
    name="$(basename "$path")"

    # Always keep the package file
    if [[ "$name" == "__init__.py" ]]; then
      echo "  + kept    $name (package)"
      continue
    fi

    # Normalize to base language name by stripping common extensions
    base="$name"
    base="${base%.abi3.so}"
    base="${base%.so}"
    base="${base%.pyd}"
    base="${base%.py}"

    keep="no"
    for k in "${KEEP_BINDINGS[@]}"; do
      if [[ "$base" == "$k" ]]; then keep="yes"; break; fi
    done

    if [[ "$keep" == "yes" ]]; then
      echo "  + kept    $name"
    else
      rm -f "$path"
      echo "  - removed $name"
    fi
  done
  shopt -u nullglob
else
  msg "No tree_sitter_language_pack bindings directory found at $BINDINGS_DIR — skipping trim."
fi

# ----------------------------
# 5) Move ripgrep binary into binary_service/bin
# ----------------------------
msg "Moving ripgrep binary into portable tree…"
DEST_PATH="$PY_DIR/$RIPGREP_DEST_REL"
mkdir -p "$(dirname "$DEST_PATH")"
cp "$RIPGREP_SRC" "$DEST_PATH"
chmod +x "$DEST_PATH"
if command -v file >/dev/null 2>&1; then
  file "$DEST_PATH" || true
fi
echo "  -> placed at $DEST_PATH"

# ----------------------------
# Optional size trim
# ----------------------------
if [[ "$STRIP_BINARIES" == "1" ]]; then
  msg "Stripping binaries to reduce size (optional)…"
  if command -v strip >/dev/null 2>&1; then
    if [[ "$OS" == "linux" ]]; then
      # On Linux: strip .so files and ripgrep binary
      find "$PY_DIR" -type f \( -name '*.so' -o -path "$DEST_PATH" \) \
        -exec strip --strip-unneeded {} + 2>/dev/null || true
    elif [[ "$OS" == "macos" ]]; then
      # On macOS: strip .so, .dylib, and ripgrep binary
      find "$PY_DIR" -type f \( -name '*.so' -o -name '*.dylib' -o -path "$DEST_PATH" \) \
        -exec strip -S -x {} + 2>/dev/null || true
    fi
  else
    warn "strip not found; skipping."
  fi
fi


# ----------------------------
# 6) Smoke test
# ----------------------------
msg "Smoke testing the embedded app… (entry point may not support --help)"
"$PYTHON" - <<'PY'
import sys, sysconfig
print("ok: using", sys.executable)
print("site-packages:", sysconfig.get_paths().get("purelib"))
PY

# ----------------------------
# 7) Package
# ----------------------------
msg "Creating tarball $PKG_TARBALL …"
# Avoid AppleDouble files (._*) in the tarball on macOS
export COPYFILE_DISABLE=1
tar -czf "$PKG_TARBALL" "$PY_DIR"


# ----------------------------
# 8) Checksum
# ----------------------------
if command -v node >/dev/null 2>&1; then
  msg "Computing checksum of $PY_DIR …"
  CHECKSUM="$(node hash-binary.js "$PY_DIR" | awk '/^Checksum:/ {print $2}')"
  if [[ -n "$CHECKSUM" ]]; then
    echo "  -> checksum is $CHECKSUM"
  else
    warn "Checksum failed or empty"
  fi
else
  warn "node not found, skipping checksum."
fi


# ----------------------------
# 9) Create binary_manifest.json
# ----------------------------
msg "Creating binary_manifest.json manifest …"

cat > binary_manifest.json <<EOF
{
  "${VERSION}": {
    "${OS}": {
      "${ARCH}": {
        "directory": "${PKG_TARBALL}",
        "file_checksum": "${CHECKSUM}",
        "file_path": "${PKG_TARBALL}/binary_service",
        "s3_key": "binaries/${VERSION}/${OS}/${PKG_TARBALL}.tar.gz",
        "service_path": "${PKG_TARBALL}/binary_service/bin/python3",
        "use_python_module": true
      }
    }
  }
}
EOF

echo "  -> wrote binary_manifest.json"


msg "Done."
du -sh "$PY_DIR" "$PKG_TARBALL" 2>/dev/null || true
echo
echo "Portable artifact: $PKG_TARBALL"
