#!/usr/bin/env bash
set -euo pipefail

# shellcheck source=/dev/null
source .venv/bin/activate

# Start Docker daemon when available so nested docker commands work inside the artifact container.
if command -v dockerd >/dev/null 2>&1; then
  export DOCKER_DATA_ROOT=/home/vscode/.docker-data
  export DOCKER_RUNTIME_DIR=/home/vscode/.docker-run
  export DOCKER_SOCKET=${DOCKER_RUNTIME_DIR}/docker.sock
  export DOCKER_HOST=unix://${DOCKER_SOCKET}
  mkdir -p "${DOCKER_DATA_ROOT}" "${DOCKER_RUNTIME_DIR}"
  dockerd \
    --data-root "${DOCKER_DATA_ROOT}" \
    --exec-root "${DOCKER_RUNTIME_DIR}/exec" \
    --pidfile "${DOCKER_RUNTIME_DIR}/dockerd.pid" \
    --host="unix://${DOCKER_SOCKET}" \
    > /tmp/dockerd.log 2>&1 &

  for _ in $(seq 1 60); do
    if [ -S "${DOCKER_SOCKET}" ] && docker -H "${DOCKER_HOST}" info >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

exec "$@"
