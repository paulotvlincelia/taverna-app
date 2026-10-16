FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python3 python3-websockets openssl ca-certificates libgmp10 libnuma1 libtinfo6 libssl3 zlib1g && rm -rf /var/lib/apt/lists/*
ENV HOME=/work
WORKDIR /work
