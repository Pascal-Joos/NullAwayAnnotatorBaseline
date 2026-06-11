# NullRepair Artifact Instructions

This README only explains how to load and connect to the artifact container.  
For the complete artifact instructions, please refer to the `README.md` inside the container at `/home/vscode/NullRepairBaseline/README.md`, once the container is running.

## 1. Requirements

Artifact was packaged as an x86_64 Docker image.

Technical requirements:

- Operating system: Linux, MacOS, or Windows. MacOS and Windows have not been tested.
- Disk space: At least 50 GB free to download the artifact, load the Docker image, and run experiments.
- Memory: At least 8 GB of RAM for running the artifact container and experiments.
- Installation of Docker. Has been tested on Linux with Docker 29.5.3.
- An OpenAI API key. This is needed to run NullRepair and the baselines, which use the OpenAI API. For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 3. and 4.).  

User requirements:

- Familiarity with Docker and Git.

## 2. Installation

### 2.1. Linux Systems

Load and run the image:

```bash
docker load -i nullrepair_artifact_image.tar
docker run --rm -it --name nullrepair_artifact -v /var/run/docker.sock:/var/run/docker.sock nullrepair-issta-artifact:latest bash
```

The run command mounts the host's Docker socket into the container and runs the artifact image as root, so the socket is accessible.  
This is needed to run the mini-SWE-agent baseline experiments, as the agent runs are executed in separate containers.

Jump to section 3. for instructions on attaching VS Code to the running container.

### 2.2. macOS Systems (Intel and Apple Silicon)

The artifact image was built for `linux/amd64`. On **Apple Silicon** (M1/M2/M3/M4), you must add `--platform linux/amd64` to run it via Rosetta emulation — expect slower execution compared to native hardware.

On macOS the Docker socket path depends on your Docker Desktop version:

- **Docker Desktop < 4.13**: `/var/run/docker.sock` (same as Linux)
- **Docker Desktop ≥ 4.13**: `~/.docker/run/docker.sock` (symlink at `/var/run/docker.sock` may or may not exist)

Check which path is available on your machine:

```bash
ls /var/run/docker.sock 2>/dev/null || echo "not found, use ~/.docker/run/docker.sock"
```

Load the image:

```bash
docker load -i nullrepair_artifact_image.tar
```

Run with the appropriate socket path. Replace `<socket>` with the path found above:

```bash
# Intel Mac
docker run --rm -it --name nullrepair_artifact \
  -v <socket>:/var/run/docker.sock \
  nullrepair-issta-artifact:latest bash

# Apple Silicon (M1/M2/M3/M4) — adds Rosetta emulation
docker run --rm -it --platform linux/amd64 --name nullrepair_artifact \
  -v <socket>:/var/run/docker.sock \
  nullrepair-issta-artifact:latest bash
```

Jump to section 3. for instructions on attaching VS Code to the running container.

### 2.3. Windows Systems

Running on Windows requires Docker Desktop with **WSL2**.

With the WSL2 backend, Docker Desktop exposes `/var/run/docker.sock` inside your WSL2 distribution, so the same command as Linux works without modification.

Prerequisites:

1. Install WSL2 and a Linux distribution (e.g. Ubuntu) from the Microsoft Store.
2. In Docker Desktop: *Settings → General* → enable **"Use the WSL 2 based engine"**.
3. In Docker Desktop: *Settings → Resources → WSL Integration* → enable integration for your distribution.

Then open a WSL2 terminal and run:

```bash
docker load -i nullrepair_artifact_image.tar
docker run --rm -it --name nullrepair_artifact -v /var/run/docker.sock:/var/run/docker.sock nullrepair-issta-artifact:latest bash
```

### 3. Attaching VS Code to the Container

You can attach VS Code to the running container using the Dev-Containers extension.  
In VS Code, open the Command Palette (Ctrl+Shift+P) and select "Dev-Containers: Attach to Running Container..." and choose `nullrepair_artifact`.

Inside the container, the repository is available at `/home/vscode/NullRepairBaseline`.  
Refer to the `README.md` (`/home/vscode/NullRepairBaseline/README.md`) inside the container for instructions on finalizing the setup of the environment, running experiments, and evaluating results.
