
import json
import re
import requests
from urllib.parse import urlparse

from app.config import GROQ_URL, TAVILY_URL


# ============================================================
# PROVIDER ERROR
# ============================================================

class ProviderError(RuntimeError):

    def __init__(self, provider, message, status_code=None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


# ============================================================
# GROQ AI JSON RESPONSE
# ============================================================

def groq_json(prompt, key, model, system, max_tokens=650):

    if not key:
        raise ProviderError(
            "Groq",
            "Groq API key is missing."
        )

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    messages = [
        {
            "role": "system",
            "content": system
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": max(4096, max_tokens * 4),
        "temperature": 0,
    }

    # GPT-OSS specific settings
    if model.startswith("openai/gpt-oss"):

        payload["reasoning_effort"] = "low"
        payload["include_reasoning"] = False

    try:

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=(10, 90)
        )

    except requests.RequestException as e:

        raise ProviderError(
            "Groq",
            f"Network error: {e}"
        ) from e

    # HTTP error handling
    if response.status_code == 401:

        raise ProviderError(
            "Groq",
            "Groq API key rejected. Check your API key.",
            401
        )

    if response.status_code == 403:

        raise ProviderError(
            "Groq",
            "Model access denied.",
            403
        )

    if response.status_code == 429:

        raise ProviderError(
            "Groq",
            "Groq rate limit or token quota reached.",
            429
        )

    if response.status_code == 413:

        raise ProviderError(
            "Groq",
            "Request payload is too large.",
            413
        )

    if response.status_code >= 400:

        raise ProviderError(
            "Groq",
            f"Groq API error {response.status_code}: "
            f"{response.text[:500]}",
            response.status_code
        )

    # Parse response
    try:

        data = response.json()

        choices = data.get("choices", [])

        if not choices:
            raise ValueError(
                "Groq returned no choices."
            )

        choice = choices[0]
        message = choice.get("message", {})

        raw = message.get("content")

        # Diagnose empty response
        if not raw or not raw.strip():

            finish_reason = choice.get("finish_reason")
            usage = data.get("usage", {})

            raise ValueError(
                "Groq returned empty content. "
                f"Finish reason: {finish_reason}. "
                f"Token usage: {usage}"
            )

        raw = raw.strip()

        # Remove Markdown code fences
        raw = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw,
            flags=re.I
        ).strip()

        # Direct JSON parsing
        try:

            result = json.loads(raw)

        except json.JSONDecodeError:

            first = raw.find("{")
            last = raw.rfind("}")

            if first == -1 or last <= first:

                raise ValueError(
                    "No valid JSON object found in model response."
                )

            result = json.loads(
                raw[first:last + 1]
            )

        if not isinstance(result, dict):

            raise ValueError(
                "Expected a JSON object from Groq."
            )

        return result

    except Exception as e:

        raise ProviderError(
            "Groq",
            f"Invalid model response: {e}"
        ) from e


# ============================================================
# SOURCE CLASSIFICATION
# ============================================================

def source_type(url):

    domain = (
        urlparse(url)
        .netloc
        .lower()
        .removeprefix("www.")
    )

    # Government domains
    if domain.endswith(
        (".gov", ".gov.uk", ".gov.in", ".gc.ca")
    ):

        return "Government"

    # Academic domains
    if domain.endswith(
        (".edu", ".ac.uk", ".edu.au")
    ):

        return "Academic"

    trusted = (
        "who.int",
        "worldbank.org",
        "imf.org",
        "un.org",
        "oecd.org",
        "nasa.gov",
        "nist.gov",
        "canada.ca",
        "asc-csa.gc.ca",
        "esa.int",
        "ec.europa.eu",
        "sec.gov",
        "bls.gov",
        "census.gov",
        "ons.gov.uk"
    )

    if any(
        domain == item or domain.endswith("." + item)
        for item in trusted
    ):

        return "Official / institutional"

    # Established media
    media = (
        "reuters.com",
        "apnews.com",
        "bbc.com",
        "ft.com",
        "nature.com",
        "science.org"
    )

    if any(
        domain == item or domain.endswith("." + item)
        for item in media
    ):

        return "Established publisher"

    return "Other — review source"


# ============================================================
# TAVILY WEB SEARCH
# ============================================================

def tavily_search(query, key, max_results=2):

    if not key:

        raise ProviderError(
            "Tavily",
            "Tavily API key is missing."
        )

    payload = {
        "api_key": key,
        "query": query[:350],
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }

    try:

        response = requests.post(
            TAVILY_URL,
            json=payload,
            timeout=(10, 45)
        )

    except requests.RequestException as e:

        raise ProviderError(
            "Tavily",
            f"Network error: {e}"
        ) from e

    if response.status_code in (401, 403):

        raise ProviderError(
            "Tavily",
            "Tavily API key rejected.",
            response.status_code
        )

    if response.status_code == 429:

        raise ProviderError(
            "Tavily",
            "Tavily rate limit or credit limit reached.",
            429
        )

    if response.status_code >= 400:

        raise ProviderError(
            "Tavily",
            f"Tavily error {response.status_code}: "
            f"{response.text[:500]}",
            response.status_code
        )

    try:

        response_data = response.json()

    except ValueError as e:

        raise ProviderError(
            "Tavily",
            "Invalid JSON response from Tavily."
        ) from e

    results = []

    for item in response_data.get("results", []):

        url = item.get("url", "")

        if not url:
            continue

        results.append({

            "title": (
                item.get("title", "")[:160]
            ),

            "url": url,

            "domain": (
                urlparse(url).netloc.lower()
            ),

            "source_type": source_type(url),

            "snippet": (
                item.get("content") or ""
            )[:500],

        })

    return results
