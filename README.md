# 🔬 AI Physics Helper

AI-powered physics assistant with:

- Arabic-first web UI
- FastAPI backend
- OpenAI Responses API
- Physics RAG / source ranking
- Image-based problem solving
- Deterministic and symbolic physics solver
- Android WebView client
- GitHub Actions APK build

## Quick start

### Backend

1. Copy `.env.example` to `.env`.
2. Set `OPENAI_API_KEY` on the server only. Never put the key in the Android app.
3. Run:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Android

The Android project uses Gradle 8.10.2 and Android Gradle Plugin 8.7.3. GitHub Actions can build the debug APK automatically.

See `CLOUD_BUILD.md` for the exact GitHub steps.

## Security

For production, serve the backend over HTTPS and add authentication/rate limiting before making it public. The Android app stores only the backend URL, not the OpenAI API key.

## Important

The project includes ingestion pipelines for physics sources. It does not bundle copyrighted books or paywalled papers. Only ingest material you have the right to use.
