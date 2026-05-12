#!/usr/bin/env bash
set -euo pipefail

# Build and export a submission-ready Docker image that contains this repository,
# initialized submodules, and freshly checked-out benchmark repositories.
#
# Usage:
#   scripts/create_artifact_image.sh [output_tar]
#
# Defaults:
#   output_tar: ./nullrepair_artifact_image.tar
#   image_tag:  nullrepair-issta-artifact:latest

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_TAR="${1:-${ROOT_DIR}/artifact/nullrepair_artifact_image.tar}"
IMAGE_TAG="${IMAGE_TAG:-nullrepair-issta-artifact:latest}"
DOCKERFILE_PATH="${ROOT_DIR}/Dockerfile.artifact"


# Initialize git submodules before building the image so the working tree is complete.
echo "Initializing git submodules..."
git -C "${ROOT_DIR}" submodule update --init --recursive

# Check out the benchmark repositories to include them in the image.
GIT_PROTOCOL=https bash "${ROOT_DIR}/checkout_benchmarks.sh"

# Resolve Docker availability early.
if ! command -v docker >/dev/null 2>&1; then
  echo "Error: docker is not installed or not on PATH." >&2
  exit 1
fi

if [ ! -f "${DOCKERFILE_PATH}" ]; then
  echo "Error: expected Dockerfile at ${DOCKERFILE_PATH}" >&2
  exit 1
fi

echo "[1/3] Building artifact image ${IMAGE_TAG}..."
docker build -f "${DOCKERFILE_PATH}" -t "${IMAGE_TAG}" "${ROOT_DIR}"

echo "[2/3] Preparing output location..."
mkdir -p "$(dirname "${OUTPUT_TAR}")"

echo "[3/3] Saving Docker image to ${OUTPUT_TAR}..."
docker save -o "${OUTPUT_TAR}" "${IMAGE_TAG}"

echo "Done."
echo "Image tag: ${IMAGE_TAG}"
echo "Archive : ${OUTPUT_TAR}"
