FROM python:3.13-bookworm

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    pkg-config \
    cmake \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY . /workspace

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir -r requirements.txt \
    bayanpy \
    infomap \
    pyclustering \
    ASLPAw \
    leidenalg \
    igraph \
    pycombo \
    GraphRicciCurvature

CMD ["python", "tools/test_crisp_algorithms.py"]
