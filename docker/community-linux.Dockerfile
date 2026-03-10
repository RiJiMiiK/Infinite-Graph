FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-graph-tool \
    python3-igraph \
    python3-numpy \
    python3-scipy \
    build-essential \
    ca-certificates \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /workspace

RUN python3 -m pip install --break-system-packages --no-cache-dir \
    networkx>=3.0 \
    cdlib>=0.4.0 \
    infomap \
    leidenalg \
    bayanpy \
    pycombo \
    GraphRicciCurvature

CMD ["python3", "tools/test_crisp_algorithms.py", "--algorithm", "sbm_dl"]
