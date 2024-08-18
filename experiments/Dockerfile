FROM chaostoolkit/chaostoolkit

LABEL maintainer="chaos-kafka <jorge.tapich@friki.io>"

USER root

# Install bash, build dependencies, and other required packages
RUN apk add --no-cache \
    bash \
    build-base \
    zlib-dev \
    bzip2-dev \
    openssl-dev \
    cyrus-sasl-dev \
    python3-dev \
    py3-pip \
    wget \
    git \
    vim

RUN git clone https://github.com/edenhill/librdkafka.git /tmp/librdkafka

RUN cd /tmp/librdkafka && git checkout v2.5.0

RUN cd /tmp/librdkafka && ./configure && make && make install

WORKDIR /experiments

ADD . .
RUN pip install --no-cache-dir -r requirements.txt

RUN rm -rf /tmp/librdkafka

ENTRYPOINT ["/usr/local/bin/chaos"]