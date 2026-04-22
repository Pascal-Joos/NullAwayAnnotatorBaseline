FROM mcr.microsoft.com/devcontainers/base:ubuntu
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git openjdk-11-jdk-headless openjdk-17-jdk-headless openjdk-17-jre openjdk-17-jdk android-sdk wget curl xvfb



# Copy Android SDK licenses
COPY ./docker_files/licenses /usr/lib/android-sdk/licenses
RUN chown -R vscode:vscode /usr/lib/android-sdk

ENV JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64
ENV ANDROID_HOME=/usr/lib/android-sdk

USER vscode
WORKDIR /home/vscode

# Install and build NullAway dependency
RUN git clone https://github.com/Pascal-Joos/NullAway.git /home/vscode/NullAway && cd /home/vscode/NullAway && git checkout d0c7d8390964ee5dc95d6bf93ae76b85913b2342 \
    && echo 'sdk.dir=/usr/lib/android-sdk' >local.properties && ./gradlew build -x test && ./gradlew publishToMavenLocal
    

CMD ["bash"]