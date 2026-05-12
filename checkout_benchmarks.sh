#!/bin/bash

# This script clones the log files repo and checks out the target projects for the experiment into `benchmarks` 
# (i.e., at the same level as the nullrepair repository).


projects=(
  "conductor"
  "eureka"
  "glide"
  "gson"
  "jadx"
  "libgdx"
  "litiengine"
  "mockito"
  "retrofit"
  "spring-boot"
  "wala-util"
  "zuul"
)

# Get current directory to return to it after cloning each project
current_dir=$(pwd)

# Allow non-interactive cloning (e.g., Docker image build) without SSH keys.
GIT_PROTOCOL=${GIT_PROTOCOL:-ssh}
if [ "$GIT_PROTOCOL" = "https" ]; then
    clone_base_url="https://github.com/Pascal-Joos"
else
    clone_base_url="git@github.com:Pascal-Joos"
fi

# Create benchmarks directory if it doesn't exist
mkdir -p benchmarks
cd benchmarks

for project in "${projects[@]}"; do
    # Only clone if the directory doesn't already exist
    if [ ! -d "$project" ]; then

        git clone "${clone_base_url}/$project.git" "$project"
        cd "$project" && git checkout nimak/auto-code-fix
        cd ..
    else
        echo "Directory $project already exists. Skipping clone."
    fi
done

# Return to the original directory
cd "$current_dir"