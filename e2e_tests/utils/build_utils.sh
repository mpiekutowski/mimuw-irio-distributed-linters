#!/bin/sh

# We are using this self-made build script instead of docker-compose --build
# because docker compose ALWAYS rebuild but docker build exits early if nothing changed.

build_image() {
  local dockerfile_path="$1"
  local image_name="$2"

  printf "\033[1mBuilding %s image...\033[0m\n" "$image_name"
  (cd "$dockerfile_path" && docker build -t "$image_name" . > /dev/null 2> /dev/null)

  # Check the exit status of the docker build command
  if [ $? -eq 0 ]; then
    printf "\033[32mBuild succeeded for %s image.\033[0m\n" "$image_name"
  else
    printf "\033[31mFailed to build %s image. Exiting.\033[0m\n" "$image_name"
    exit 1
  fi
}