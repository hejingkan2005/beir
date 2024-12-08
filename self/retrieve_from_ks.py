from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from urllib.parse import parse_qs, urlparse
import json
import requests

def fetch_knowledge_service_response(
    token: str,
    query: str,
    endpoint: str,
    category: str,
    scope: str,
    top: int,
    threshold: float,
) -> str:
    # Asserts
    assert category in {
        "document",
        "training",
        "evaluation",
    }, f"Invalid category {category}"
    assert top > 0, f"Invalid top {top} when invoke knowledge service, must be > 0."
    assert (
        0 <= threshold <= 1
    ), f"Invalid threshold {threshold} when invoke knowledge service, must be [0, 1]."

    # if endpoint.startswith("https://learn.microsoft.com"):
    #     assert (
    #         category != "evaluation"
    #     ), "Evaluation category is not supported in public KS."

    # Fetch response
    endpoint_url = endpoint.replace("{category}", category)
    endpoint_url_parsed = urlparse(endpoint_url)

    url_params = parse_qs(endpoint_url_parsed.query)
    endpoint_url_parsed = endpoint_url_parsed._replace(params="", query="", fragment="")

    request_params = {
        "url": endpoint_url_parsed.geturl(),
        "json": {
            "input": query,
        },
        "headers": {"Authorization": f"Bearer {token}"},
        "params": {
            **url_params,
            "top": top,
            "scorethreshold": threshold,
        },
    }

    use_api_v2 = category == "document"
    if use_api_v2:
        request_params["params"]["api-version"] = "v2"
    # if scope is not None or scope.strip("\n ") != "":
    #     request_params["params"]["scope"] = scope

    # response = post_request(request_params=request_params)
    response = requests.post(
        request_params["url"],
        json=request_params["json"],
        headers=request_params["headers"],
        params=request_params["params"],
    )
    response.raise_for_status()

    # return convert_v2_to_v1(response.json()) if use_api_v2 else response.json()
    return (response.json())

def retrieve_from_ks(
    token: str,
    query: str,
    endpoint: str,
    ks_category: str = "document",
    ks_scope: str = None,  # type: ignore
    ks_top: int = 5,
    ks_threshold: float = 0.8,
) -> str:

    # try:
    #     ks_const = json.loads(ks_source)

    #     if isinstance(ks_const, list):
    #         if validate_ks_const(ks_const):
    #             return ks_const
    # except AssertionError as e:
    #     raise e
    # except Exception:
    #     pass

    return fetch_knowledge_service_response(
        token,
        query,
        endpoint,
        ks_category,
        ks_scope,
        ks_top,
        threshold=ks_threshold,
    )

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "api://5405974b-a0ac-4de0-80e0-9efe337ea291/.default"
)

response = retrieve_from_ks(token_provider(), "what is azure cognitive services", "https://learn.microsoft.com/api/knowledge/document/relevantitems", "document", None, 5, 0.8)

print(response)
