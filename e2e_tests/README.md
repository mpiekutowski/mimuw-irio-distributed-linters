## Run all end to end tests

`./run_all_tests.sh`

## Run one of the tests

`cd machine_manager && ./test.sh`

**Important** - try not to kill tests with Ctrl+C as it will not run `docker compose down`. You may need to remove the containers and network manually after that.

## Add new tests
Look at example test provided in `sanity_check` directory. Provide `test.sh` script. Use functions defined in `utils/` directory to make it easier. Place any mock services needed in `utils/` directory.

After the scripts are ready add your directory to `run_all_tests.sh`.