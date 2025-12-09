FROM mcr.microsoft.com/devcontainers/base:ubuntu
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv git openjdk-11-jdk-headless openjdk-17-jdk-headless openjdk-17-jre openjdk-17-jdk android-sdk wget curl xvfb

# Install JDK 23. Temporarily needed for NullAway build, as the server providing it for NullAway is down.
RUN wget -O /tmp/openjdk-23.tar.gz https://download.java.net/java/GA/jdk23.0.2/6da2a6609d6e406f85c491fcb119101b/7/GPL/openjdk-23.0.2_linux-x64_bin.tar.gz && \
    mkdir -p /usr/lib/jvm && \
    tar -xzf /tmp/openjdk-23.tar.gz -C /usr/lib/jvm && \
    rm -f /tmp/openjdk-23.tar.gz


# Copy Android SDK licenses
COPY ./docker_files/licenses /usr/lib/android-sdk/licenses
RUN chown -R vscode:vscode /usr/lib/android-sdk

ENV JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64
ENV ANDROID_HOME=/usr/lib/android-sdk
ENV PATH=$JAVA_HOME/bin:/usr/lib/jvm/jdk-23.0.2/bin:$PATH

USER vscode
WORKDIR /home/vscode

# Install and build NullAway dependency
RUN git clone https://github.com/nimakarimipour/NullAway.git /home/vscode/NullAway && cd /home/vscode/NullAway && git checkout d0c7d8390964ee5dc95d6bf93ae76b85913b2342 \
    && echo 'sdk.dir=/usr/lib/android-sdk' >local.properties && ./gradlew build -x test && ./gradlew publishToMavenLocal
    

CMD ["bash"]