# Records demo/demo.gif with VHS (https://github.com/charmbracelet/vhs).
# From the repository root:
#   python -m build sdk -w -o demo/
#   docker build -t opengpl-vhs demo
#   docker run --rm -v "$PWD/demo":/work -w /work opengpl-vhs demo.tape
FROM ghcr.io/charmbracelet/vhs
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-pip python3-venv jq \
 && rm -rf /var/lib/apt/lists/*
COPY opengpl_sdk-*.whl /tmp/
RUN python3 -m venv /opt/opengpl && /opt/opengpl/bin/pip install --no-cache-dir /tmp/opengpl_sdk-*.whl
ENV PATH=/opt/opengpl/bin:$PATH
