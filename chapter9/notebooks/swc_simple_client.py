import backoff
import logging
import httpx

HEALTH_CHECK_ENDPOINT = "/"
LIST_LEAGUES_ENDPOINT = "/V0/leagues/"
LIST_PLAYERS_ENDPOINT = "/v0/players/"
LIST_PERFORMANCES_ENDPOINT = "/v0/performances/"
LIST_TEAMS_ENDPOINT = "/v0/teams/"
LIST_WEEKS_ENDPOINT = "/v0/weeks/"
GET_COUNTS_ENDPOINT = "/v0/counts/"

logger = logging.getLogger(__name__)

@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=(httpx.RequestError, httpx.HTTPStatusError),
    max_time=5,
    jitter=backoff.random_jitter
)

def call_api_endpoint(
    base_url: str,
    api_endpoint: str,
    api_params: dict = None
) -> httpx.Response:

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }
        with httpx.Client(base_url=base_url, follow_redirects=True, headers=headers) as client:
            logger.debug(f"base_url: {base_url}, api_endpoint: {api_endpoint}")
            response = client.get(api_endpoint, params=api_params)
            if response.status_code >= 400:
                response.raise_for_status()
            try:
                logger.debug(f"Response JSON: {response.json()}")
            except Exception:
                logger.debug(f"Response text: {response.text}")
            return response
    except httpx.HTTPStatusError as e:
        logger.error(f"Request error occurred: {str(e)}")
        return httpx.Response(status_code=e.response.status_code, content=b"API error")
    except httpx.RequestError as e:
        logger.error(f"Request error occurred: {str(e)}")
        return httpx.Response(status_code=500, content=b"Network error")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)
        print(f"DEBUG: Exception type: {type(e)}, Message: {str(e)}")
        return httpx.Response(status_code=500, content=b"Unexpected error")
