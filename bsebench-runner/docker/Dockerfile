FROM python:3.12-slim

LABEL org.opencontainers.image.title="BSEBench external reproduction runner"
LABEL org.opencontainers.image.description="Auditable container for reproducing BSEBench result bundles"
LABEL org.opencontainers.image.vendor="BSEBench"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV BSEBENCH_HOME=/opt/bsebench
ENV BSEBENCH_REPOS_DIR=/opt/bsebench/repos
ENV BSEBENCH_BUNDLES_DIR=/opt/bsebench/bundles
ENV BSEBENCH_WORK_DIR=/opt/bsebench/work

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        libffi-dev \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install \
        numpy \
        pandas \
        scipy \
        pyyaml \
        jsonschema \
        typer \
        rich \
        pytest \
        ruff \
        mypy \
        opentimestamps-client \
        weasyprint

WORKDIR /opt/bsebench-runner

COPY bsebench-runner/runner ./runner
COPY bsebench-runner/docker/scripts ./docker/scripts
COPY bsebench-runner/repositories.example.yaml ./repositories.example.yaml

RUN chmod +x docker/scripts/*.sh runner/bsebench.py \
    && ln -s /opt/bsebench-runner/runner/bsebench.py /usr/local/bin/bsebench

ENTRYPOINT ["/opt/bsebench-runner/docker/scripts/entrypoint.sh"]
CMD ["bsebench", "--help"]
