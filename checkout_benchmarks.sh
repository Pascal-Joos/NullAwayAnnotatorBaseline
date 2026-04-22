# !/bin/bash

# This script checks out the target projects for the experiment into `../nullness-benchmarks` 
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
)

# Get current directory to return to it after cloning each project
current_dir=$(pwd)

# Create nullness-benchmarks directory if it doesn't exist
mkdir -p ../nullness-benchmarks
cd ../nullness-benchmarks

for project in "${projects[@]}"; do
    # Only clone if the directory doesn't already exist
    if [ ! -d "$project" ]; then

        git clone "git@github.com:Pascal-Joos/$project.git" "$project"
        cd "$project" && git checkout nimak/auto-code-fix
        cd ..
    else
        echo "Directory $project already exists. Skipping clone."
    fi
done

# Return to the original directory
cd "$current_dir"