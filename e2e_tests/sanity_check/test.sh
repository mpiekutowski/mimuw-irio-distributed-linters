#!/bin/bash

# Import compose_and_sleep shell function
. ./../utils/run_utils.sh

compose_and_sleep

execute_in_test_client "test-client" "pytest -v -x /tests"

exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo -e "\e[32mAll tests passed.\e[0m"
else
  echo -e "\e[31mSome tests failed.\e[0m"
fi

stop_containers

exit $exit_code