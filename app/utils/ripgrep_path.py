import platform
import stat
import sys
from pathlib import Path


def ensure_executable(path: Path) -> None:
    """Ensure the binary is executable (required during dev mode)."""
    if path.exists():
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IEXEC)


def get_project_root(marker: str = "pyproject.toml") -> Path:
    """
    Walk up the directory tree until we find a marker file (e.g., pyproject.toml).
    This is more robust than assuming a fixed folder depth.
    """
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / marker).exists():
            return current
        current = current.parent
    raise RuntimeError(f"Could not find project root with marker: {marker}")


def get_rg_path() -> str:
    """Return the path to the correct ripgrep binary based on platform and environment."""

    if "__compiled__" in globals():
        # Nuitka compiled binary
        base_dir = Path(sys.executable).parent
        rg_path = base_dir / "bin" / "rg"
    else:
        # Development mode
        system = platform.system().lower()
        machine = platform.machine().lower()

        rg_map = {
            ("darwin", "arm64"): "rg_darwin_arm",
            ("darwin", "x86_64"): "rg_darwin_x64",
            ("linux", "x86_64"): "rg_linux_x64",
            ("windows", "amd64"): "rg_win_64.exe",
        }

        binary_name = rg_map.get((system, machine))
        if not binary_name:
            raise RuntimeError(f"Unsupported platform: {system} on {machine}")
        base_dir = Path(sys.executable).parent
        rg_path = (base_dir / binary_name).resolve()
        if not rg_path.exists():
            # fallback: look in repo root /ripgrep/ (dev mode)
            project_root = get_project_root()
            rg_path = (project_root / "ripgrep" / binary_name).resolve()

    ensure_executable(rg_path)
    return str(rg_path)
