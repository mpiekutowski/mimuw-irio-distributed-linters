#!/bin/sh

compose_and_sleep() {
  local sleep_duration=10

  echo -e "Starting containers..."
  docker compose up -d > /dev/null 2> /dev/null

  if [ $? -eq 0 ]; then
    echo -e "Containers started."
  else
    echo -e "Failed to start containers. Exiting."
    exit 1
  fi

  echo "Sleeping for $sleep_duration seconds to allow the containers to start"
  sleep "$sleep_duration"
}


# Use docker exec instead of specyfiying command in docker-compose.
# With this approach we can kill both containers when tests end, 
# otherwise machine manager would be running indefinitely.
execute_in_test_client() {
  local container_name="$1"
  local test_command="$2"

  echo "Executing command in $container_name container: $test_command"
  docker exec -it "$container_name" bash -c "$test_command"
}

stop_containers() {
  echo -e "Stopping containers..."
  docker compose down > /dev/null 2> /dev/null

  if [ $? -eq 0 ]; then
    echo -e "Containers stopped."
  else
    echo -e "Failed to stop containers. Exiting."
    exit 1
  fi
}