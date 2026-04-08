#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: scripts/deploy.sh [--config-path PATH] [--container-name NAME] [--image-name NAME] [--dockerfile PATH] [--skip-pull] [--skip-prune]"
  echo
  echo "Deploy the wstools Discord bot with Docker."
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd -P)"
CONFIG_PATH="${REPO_DIR}/config.json"
CONTAINER_NAME="wstools-bot"
IMAGE_NAME="wstools-bot"
DOCKERFILE_PATH="${REPO_DIR}/Dockerfile"
SKIP_PULL=0
SKIP_PRUNE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config-path)
      CONFIG_PATH="$2"
      shift 2
      ;;
    --container-name)
      CONTAINER_NAME="$2"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --dockerfile)
      DOCKERFILE_PATH="$2"
      shift 2
      ;;
    --skip-pull)
      SKIP_PULL=1
      shift
      ;;
    --skip-prune)
      SKIP_PRUNE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

require_command docker
require_command git
require_command realpath

CONFIG_PATH="$(realpath "${CONFIG_PATH}")"
DOCKERFILE_PATH="$(realpath "${DOCKERFILE_PATH}")"

if [[ ! -f "${CONFIG_PATH}" ]]; then
  echo "Config file does not exist: ${CONFIG_PATH}" >&2
  exit 1
fi

if [[ ! -f "${DOCKERFILE_PATH}" ]]; then
  echo "Dockerfile does not exist: ${DOCKERFILE_PATH}" >&2
  exit 1
fi

cd "${REPO_DIR}"

echo "Starting deployment..."

if [[ "${SKIP_PULL}" -eq 0 ]]; then
  echo "Pulling latest changes from Git..."
  git pull --ff-only
fi

echo "Building Docker image..."
docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE_PATH}" .

echo "Replacing container..."
if [[ "$(docker ps -aq -f "name=^${CONTAINER_NAME}$")" ]]; then
  echo "Stopping and removing old container..."
  docker stop "${CONTAINER_NAME}"
  docker rm "${CONTAINER_NAME}"
fi

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart always \
  -v "${CONFIG_PATH}:/app/config.json:ro" \
  "${IMAGE_NAME}"

if [[ "${SKIP_PRUNE}" -eq 0 ]]; then
  echo "Cleaning up old images..."
  docker image prune -f
fi

echo "Deployment complete. Bot is now running."
echo "You can view logs with: docker logs -f ${CONTAINER_NAME}"
