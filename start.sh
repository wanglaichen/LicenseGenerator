#!/usr/bin/env bash
# RegMachine Web 本地启动（Git Bash / macOS / Linux）
#
# 用法:
#   ./start.sh
#   ./start.sh --kill          # 端口占用时结束旧进程后再启动
#   bash start.sh --kill
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

KILL_PORT=0
for arg in "$@"; do
    case "$arg" in
        -k|--kill)
            KILL_PORT=1
            ;;
        -h|--help)
            echo "用法: ./start.sh [--kill]"
            echo "  --kill, -k    APP_PORT 被占用时自动结束旧进程"
            exit 0
            ;;
        *)
            echo "未知参数: $arg" >&2
            echo "用法: ./start.sh [--kill]" >&2
            exit 1
            ;;
    esac
done

if [[ -f ".env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source ".env"
    set +a
fi

export APP_HOST="${APP_HOST:-0.0.0.0}"
export APP_PORT="${APP_PORT:-9212}"

is_windows_shell() {
    [[ "${OSTYPE:-}" == msys* || "${OSTYPE:-}" == cygwin* || "${OSTYPE:-}" == win32* ]]
}

python_has_deps() {
    "$1" -c "import flask" >/dev/null 2>&1
}

python_has_pip() {
    "$1" -m pip --version >/dev/null 2>&1
}

ensure_python() {
    # 已显式指定解释器则直接用它
    if [[ -n "${PYTHON_BIN:-}" ]]; then
        if python_has_deps "$PYTHON_BIN"; then
            return 0
        fi
        if python_has_pip "$PYTHON_BIN"; then
            echo "Installing Python dependencies from requirements.txt..."
            "$PYTHON_BIN" -m pip install -r "$ROOT_DIR/requirements.txt"
        fi
        if python_has_deps "$PYTHON_BIN"; then
            return 0
        fi
        echo "Python dependencies (flask) are not available in $PYTHON_BIN." >&2
        exit 1
    fi

    # 收集候选解释器：PATH + Windows py launcher + 常见安装路径
    local candidates=()
    local cmd
    for cmd in python.exe python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            candidates+=("$(command -v "$cmd")")
        fi
    done
    if command -v py.exe >/dev/null 2>&1; then
        while IFS= read -r path; do
            [[ -n "$path" && -x "$path" ]] && candidates+=("$path")
        done < <(py.exe -0p 2>/dev/null | awk '{print $NF}')
    elif command -v py >/dev/null 2>&1; then
        while IFS= read -r path; do
            [[ -n "$path" && -x "$path" ]] && candidates+=("$path")
        done < <(py -0p 2>/dev/null | awk '{print $NF}')
    fi

    local user_dir="${USERNAME:-${USER:-}}"
    if [[ -z "$user_dir" ]]; then
        user_dir="$(whoami 2>/dev/null || echo '')"
    fi
    local p
    for p in \
        "/c/Users/${user_dir}/AppData/Local/Programs/Python/Python313/python.exe" \
        "/c/Users/${user_dir}/AppData/Local/Programs/Python/Python312/python.exe" \
        "/c/Users/${user_dir}/AppData/Local/Programs/Python/Python311/python.exe" \
        "/c/Program Files/Python313/python.exe" \
        "/c/Program Files/Python312/python.exe" \
        "/c/Program Files/Python311/python.exe"; do
        [[ -x "$p" ]] && candidates+=("$p")
    done

    # 1) 优先挑选已装好 flask 的解释器，避免无谓 pip install
    local cand
    for cand in "${candidates[@]}"; do
        if python_has_deps "$cand"; then
            PYTHON_BIN="$cand"
            echo "Using Python: $PYTHON_BIN"
            return 0
        fi
    done

    # 2) 退而求其次：找一个有 pip 的解释器来安装依赖
    for cand in "${candidates[@]}"; do
        if python_has_pip "$cand"; then
            echo "Installing Python dependencies into: $cand"
            "$cand" -m pip install -r "$ROOT_DIR/requirements.txt"
            if python_has_deps "$cand"; then
                PYTHON_BIN="$cand"
                echo "Using Python: $PYTHON_BIN"
                return 0
            fi
        fi
    done

    echo "No usable Python interpreter with flask was found." >&2
    echo "Candidates checked:" >&2
    printf '  %s\n' "${candidates[@]}" >&2
    echo "Install Python 3, then: py -3 -m pip install -r requirements.txt" >&2
    exit 1
}

port_in_use() {
    local port="${1:-}"
    [[ -z "$port" ]] && return 1
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti tcp:"$port" >/dev/null 2>&1
    elif command -v ss >/dev/null 2>&1; then
        ss -ltn 2>/dev/null | grep -q ":${port} "
    elif command -v netstat >/dev/null 2>&1; then
        netstat -ano 2>/dev/null | grep -qE ":${port}[[:space:]]+.*LISTEN"
    else
        return 1
    fi
}

kill_process_tree() {
    local pid="${1:-}"
    [[ -z "$pid" ]] && return 0
    if is_windows_shell; then
        powershell -Command "Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue" >/dev/null 2>&1 || true
    else
        kill -TERM "$pid" >/dev/null 2>&1 || true
        sleep 1
        kill -KILL "$pid" >/dev/null 2>&1 || true
    fi
}

stop_old_listener() {
    local port="${APP_PORT}"
    local pids=()

    if ! port_in_use "$port"; then
        return 0
    fi

    if command -v lsof >/dev/null 2>&1; then
        mapfile -t pids < <(lsof -ti tcp:"$port" 2>/dev/null || true)
    elif command -v netstat >/dev/null 2>&1; then
        mapfile -t pids < <(netstat -ano 2>/dev/null | awk -v target=":${port}" '
            $0 ~ target && ($0 ~ /LISTENING/ || $0 ~ /LISTEN/) {
                print $NF
            }
        ' || true)
    fi

    if [[ ${#pids[@]} -eq 0 ]]; then
        echo "Port ${port} is in use, but PID could not be resolved." >&2
        return 1
    fi

    local unique_pids=()
    local pid
    for pid in "${pids[@]}"; do
        if [[ -n "$pid" && "$pid" != "0" && ! " ${unique_pids[*]} " =~ " ${pid} " ]]; then
            unique_pids+=("$pid")
        fi
    done

    echo "Stopping existing process(es) on port ${port}: ${unique_pids[*]}"
    for pid in "${unique_pids[@]}"; do
        kill_process_tree "$pid"
    done
}

ensure_python

if [[ "$KILL_PORT" -eq 1 ]]; then
    stop_old_listener || true
fi

echo "Starting RegMachine Web: http://127.0.0.1:${APP_PORT}"
exec "$PYTHON_BIN" -u app.py
