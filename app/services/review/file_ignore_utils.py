import fnmatch

IGNORED_PATTERNS = [
    # Python
    "__pycache__/*", "*.pyc", "*.pyo", "*.egg-info/*", "*.eggs/*", ".coverage", ".coverage.*",
    ".pytest_cache/*", ".mypy_cache/*", ".env", ".venv/*", ".env.*", "uv.lock", "poetry.lock"

    # JavaScript / TypeScript
    "node_modules/*", "dist/*", "build/*", "*.log", "*.min.js", "*.js.map", "yarn.lock", "package-lock.json",

    # Java / Kotlin
    "target/*", "build/*", "*.class", "*.jar", "*.war", "*.ear", "*.iml", ".idea/*", ".gradle/*", "out/*",

    # Go
    "vendor/*", "bin/*", "*.test", "*.exe", "*.mod", "*.sum",

    # C/C++
    "*.o", "*.obj", "*.so", "*.dll", "*.exe", "*.out", "build/*", "cmake-build-*/*", "Makefile",

    # Rust
    "target/*", "Cargo.lock", "*.rlib",

    # Ruby
    "*.gem", ".bundle/*", "vendor/bundle/*", "log/*", "tmp/*",

    # PHP
    "vendor/*", "composer.lock", "*.log",

    # Swift / Obj-C
    "*.xcworkspace", "*.xcodeproj/*", "Pods/*", "DerivedData/*", "*.pbxproj", "build/*",

    # Android
    "*.apk", "*.dex", "*.iml", "build/*", ".gradle/*", ".idea/*",

    # Dotnet / C#
    "bin/*", "obj/*", "*.dll", "*.pdb", "*.exe", "*.user", "*.suo", ".vs/*",

    # Docker / Infra / CI
    "docker-compose.override.yml", "*.lock", "*.tfstate*", "*.log",

    # Binary / Data
    "*.csv", "*.parquet", "*.db", "*.sqlite", "*.h5", "*.zip", "*.tar.gz", "*.pdf",
    "*.png", "*.jpg", "*.jpeg", "*.mp4", "*.gif", "*.svg", "*.webp", 
    "*.ico", "*.woff", "*.woff2", "*.ttf", "*.eot",
]

def should_ignore_file(file_path: str) -> bool:
    """
    Returns True if the file matches an ignore pattern and should be skipped in PR review.
    """
    normalized_path = file_path.replace("\\", "/")
    for pattern in IGNORED_PATTERNS:
        if fnmatch.fnmatch(normalized_path, pattern):
            return True
    return False
