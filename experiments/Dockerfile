FROM python:3.11-slim

LABEL maintainer="chaos-kafka <jorge.tapich@friki.io>"

RUN groupadd -g 1001 chaos
RUN useradd -m -d /home/chaos -u 1001 -g chaos chaos

WORKDIR /chaos

ADD . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/usr/local/bin/chaos"]
CMD ["--help"]