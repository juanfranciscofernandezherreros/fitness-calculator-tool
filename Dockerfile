FROM docker.n8n.io/n8nio/n8n:latest-debian

USER root

# Install Java 21, Maven, Python 3 and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-21-jdk \
        maven \
        python3 \
        python3-pip \
        python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME and update PATH so java, mvn, python3 and node are all available
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER node
