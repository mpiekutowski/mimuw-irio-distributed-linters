#!/bin/sh

TEST_DIRECTORIES="sanity_check"

for dir in $TEST_DIRECTORIES; do
    if [ -d "$dir" ]; then
        printf "\033[1mBuilding %s using build.sh\033[0m\n" "$dir"
        # Assuming build.sh is in each directory
        (cd "$dir" && ./build.sh)
        
        # Check the exit status of the build.sh command
        if [ $? -eq 0 ]; then
            printf "\033[32mBuild succeeded for %s. Calling test.sh\033[0m\n" "$dir"
            # Assuming test.sh is in each directory
            (cd "$dir" && ./test.sh)
            
            # Check the exit status of the test.sh command
            if [ $? -eq 0 ]; then
                printf "Completed test.sh in %s\n" "$dir"
            else
                printf "\033[31mtest.sh failed in %s. Exiting.\033[0m\n" "$dir"
                exit 1  # This will terminate the entire script with exit code 1
            fi
        else
            printf "\033[31mBuild failed for %s. Skipping test.sh.\033[0m\n" "$dir"
        fi
    else
        echo "Directory $dir does not exist."
    fi
done

printf "\033[32mAll test.sh commands completed successfully.\033[0m\n"
