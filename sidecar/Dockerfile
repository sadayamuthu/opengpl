FROM python:3.11-slim

WORKDIR /app

# Install SDK from local source (monorepo build context is repo root)
COPY sdk/ /build/sdk/
RUN pip install --no-cache-dir /build/sdk/ && \
    python -m spacy download en_core_web_lg

# Copy sidecar app
COPY sidecar/api.py /app/api.py

# Policy files are mounted at /policies by the user
RUN mkdir -p /policies

EXPOSE 8080

ENV OPENGPL_POLICY_DIR=/policies

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]
