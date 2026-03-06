# OpenGPL Sidecar

Self-hosted Docker container that enforces OpenGPL policies as an HTTP sidecar.

## Usage

```bash
docker run \
  -v ./my-policy.gpl:/policies/policy.gpl:ro \
  -p 8080:8080 \
  opengpl/sidecar:latest
```

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check |
| `/input/check` | POST | Enforce input gate before sending to LLM |
| `/output/check` | POST | Enforce output gate before returning to user |

## Example

```bash
curl -X POST http://localhost:8080/input/check \
  -H "Content-Type: application/json" \
  -d '{"policy": "policy.gpl", "prompt": "What is my account balance?"}'
```

Response:
```json
{"passed": true, "action": "ALLOW", "reasons": []}
```

## Building locally

From the repo root:
```bash
docker build -f sidecar/Dockerfile -t opengpl/sidecar:dev .
```

## Known limitations

**Policy hot-reload:** The sidecar caches loaded policies for the lifetime of the process. If you update a mounted policy file, restart the container to pick up changes.
