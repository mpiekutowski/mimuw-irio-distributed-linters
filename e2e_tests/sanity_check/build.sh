#!/bin/sh

# Import build_image shell function
. ./../utils/build_utils.sh

build_image "../../machine_manager" "machine-manager"
build_image "../utils/test_client" "test-client"