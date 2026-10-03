"""Process-local direct download policy; never fall back to a paid proxy."""
import os
from urllib.parse import urlsplit


def configure_direct_downloads():
    # Do not change shell profiles, the Codex connection, or other processes.
    for key in tuple(os.environ):
        if key.lower() in {"http_proxy", "https_proxy", "all_proxy"}:
            os.environ.pop(key)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    endpoint = os.environ.get("PRAG_DOWNLOAD_ENDPOINT", "https://hf-mirror.com").rstrip("/")
    parsed = urlsplit(endpoint)
    if (parsed.scheme != "https" or parsed.username or parsed.password
            or parsed.netloc not in {"hf-mirror.com", "huggingface.co"}
            or parsed.path or parsed.query or parsed.fragment):
        raise ValueError("Choose a supported HTTPS download endpoint without credentials")
    os.environ["HF_ENDPOINT"] = endpoint
    import requests
    from huggingface_hub import configure_http_backend

    def backend():
        session = requests.Session()
        # Applies to API requests AND redirected CDN requests, including retries.
        session.trust_env = False
        return session

    configure_http_backend(backend_factory=backend)
    return endpoint
