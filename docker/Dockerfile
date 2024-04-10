FROM infer/docker/master-java

RUN apt-get update && \
    mkdir -p /usr/share/man/man1 && \
    apt-get install --yes --no-install-recommends \
      python3 \
      python-dotenv \
      openai \
      rm -rf /var/lib/apt/lists/* \

CMD ["python3", "main.py"]
