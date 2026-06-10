# NullRepair Artifact Instructions

## 1. Connecting to the Artifact Container

### 1.1 Requirements

Technical requirements:

- Operating system: Linux version >= x; MacOS and Windows have not been tested.
- Installation of Docker. Has been tested on Linux with Docker 29.4.1.
- An OpenAI API key. This is needed to run NullRepair and the baselines, which use the OpenAI API. For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 3. and 4.).  

User requirements:

- Familiarity with Docker and Git.

### 1.2 Installation

Load and run the image:

```bash
docker load -i nullrepair_artifact_image.tar
docker run --rm -it --name nullrepair_artifact -v /var/run/docker.sock:/var/run/docker.sock nullrepair-issta-artifact:latest bash
```

The run command mounts the host's Docker socket into the container and runs the artifact image as root, so the socket is accessible.  
This is needed to run the mini-SWE-agent baseline experiments as the agent runs are executed in separate containers.

You can attach VS Code to the running container using the Dev-Containers extension.  
In VS Code, open the Command Palette (Ctrl+Shift+P) and select "Dev-Containers: Attach to Running Container..." and choose `nullrepair_artifact`.

Inside the container, the repository is available at `/home/vscode/NullRepairBaseline`.  
Refer to the `README.md` (`/home/vscode/NullRepairBaseline/README.md`) inside the container for instructions on finalizing the setup of the environment, running experiments, and evaluating results.
