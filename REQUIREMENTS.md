# Requirements

Artifact was packaged as an x86_64 Docker image.

Technical requirements:

- Operating system: Linux, MacOS, or Windows. MacOS and Windows have not been tested.
- Disk space: At least 50 GB free to download the artifact, load the Docker image, and run experiments.
- Memory: At least 8 GB of RAM for running the artifact container and experiments.
- Installation of Docker. Has been tested on Linux with Docker 29.5.3.
- An OpenAI API key. This is needed to run NullRepair and the baselines, which use the OpenAI API. For a lightweight reproduction of the experiment results from the log files, the API key is not needed (see 3. and 4.).  

User requirements:

- Familiarity with Docker and Git.
