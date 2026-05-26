# Audio Fixtures

The stable public demo path uses sanitized fixture metadata instead of raw user recordings. Each `*.fixture.json` entry represents one reproducible spoken command, its expected transcript, and the local or controlled page target. Raw audio generated during local demos is ignored by `.gitignore`.

Fixture manifests are replayed through the fixture endpoint or trace-generation script, not uploaded as audio:

```bash
curl -X POST http://127.0.0.1:8000/api/fixtures/icon-search/executions
uv run python scripts/generate_demo_traces.py
```
