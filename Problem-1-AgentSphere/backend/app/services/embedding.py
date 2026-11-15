
import httpx

from fastapi import HTTPException
from app.core.config import settings


def generate_embedding(text: str) -> list[float]:

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured."
        )

    try:
        response = httpx.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent",
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "Content-Type": "application/json"
            },
            json={
                "content": {
                    "parts": [{"text": text}]
                },
                "output_dimensionality": 1536
            },
            timeout=30.0
        )

        response.raise_for_status()

        embedding = response.json()["embedding"]["values"]

        if len(embedding) != 1536:
            raise ValueError("Unexpected embedding dimensions.")

        return embedding

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Gemini returned HTTP "
                f"{exc.response.status_code}: "
                f"{exc.response.text[:500]}"
            )
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to Gemini API."
        )

    except (KeyError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Invalid Gemini embedding response."
        )
