#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  scripts/publish.sh [--check|--dry-run]

By default this builds, validates, and uploads the current pyproject.toml
version to PyPI. Use --check or --dry-run to build and validate without
uploading.
EOF
}

version="$(python3 - <<'PY'
try:
    import tomllib
except ModuleNotFoundError:
    import toml as tomllib

with open("pyproject.toml", "r", encoding="utf-8") as handle:
    print(tomllib.loads(handle.read())["project"]["version"])
PY
)"

upload=true
case "${1:-}" in
    "")
        ;;
    "--upload")
        ;;
    "--check"|"--dry-run")
        upload=false
        ;;
    "-h"|"--help")
        usage
        exit 0
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac

has_pypirc_credentials() {
    local pypirc="${PYPIRC_PATH:-$HOME/.pypirc}"

    [[ -f "$pypirc" ]] || return 1
    grep -Eq '^[[:space:]]*username[[:space:]]*=' "$pypirc" || return 1
    grep -Eq '^[[:space:]]*password[[:space:]]*=' "$pypirc" || return 1
}

ensure_pypi_credentials() {
    if [[ -n "${TWINE_PASSWORD:-}" ]]; then
        export TWINE_USERNAME="${TWINE_USERNAME:-__token__}"
        return
    fi

    if has_pypirc_credentials; then
        return
    fi

    if [[ ! -t 0 ]]; then
        echo "PyPI credentials were not found." >&2
        echo "Set TWINE_USERNAME=__token__ and TWINE_PASSWORD, or add ~/.pypirc." >&2
        return 1
    fi

    echo "PyPI API token was not found in TWINE_PASSWORD or ~/.pypirc."
    read -r -s -p "Enter PyPI API token: " pypi_token
    echo

    if [[ -z "$pypi_token" ]]; then
        echo "No token entered; aborting upload." >&2
        return 1
    fi

    export TWINE_USERNAME="__token__"
    export TWINE_PASSWORD="$pypi_token"
}

python3 -m build
python3 -m twine check "dist/torbot-${version}"*
if [[ "$upload" == true ]]; then
    ensure_pypi_credentials
    python3 -m twine upload "dist/torbot-${version}"*
else
    echo "Package artifacts for torbot ${version} are ready."
    echo "Run scripts/publish.sh to upload them to PyPI."
fi
