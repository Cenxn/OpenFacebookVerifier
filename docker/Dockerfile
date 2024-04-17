FROM debian:bullseye-slim

# mkdir the man/man1 directory due to Debian bug #863199
RUN apt-get update && \
    mkdir -p /usr/share/man/man1 && \
    apt-get install --yes --no-install-recommends \
      curl \
      libc6-dev \
      openjdk-11-jdk-headless \
      sqlite3 \
      xz-utils \
      zlib1g-dev \
      python3 \
      python3-pip \
      git && \
    rm -rf /var/lib/apt/lists/*

# Download the Infer release
RUN INFER_VERSION=v1.1.0; \
    cd /opt && \
    curl -sL \
      https://github.com/facebook/infer/releases/download/${INFER_VERSION}/infer-linux64-${INFER_VERSION}.tar.xz | \
    tar xJ && \
    rm -f /infer && \
    ln -s ${PWD}/infer-linux64-$INFER_VERSION /infer

# Install python-dotenv and openai packages
RUN pip3 install python-dotenv openai

# Install script
RUN cd / && \
    git clone https://github.com/Cenxn/OpenFacebookVerifier.git

# Install infer
ENV PATH /infer/bin:${PATH}

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
