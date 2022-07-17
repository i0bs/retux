from enum import Enum
from json import dumps, loads
from logging import INFO, getLogger
from sys import version_info
from typing import Protocol

from attrs import define, field
from httpx import QueryParams, Response
from httpx import __version__ as __http_version__
from httpx import delete, get, post, put
from trio import Event, sleep_until

from retux.api.error import HTTPException

from ..const import MISSING, NotNeeded, __api_url__, __repo_url__, __version__

logger = getLogger(__name__)


class _RouteMethod(Enum):
    """Represents the types of route methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


@define(repr=False, slots=False)
class _Route:
    """
    Represents a route path to an API endpoint.

    By standard nature, the route will only contain the relevant sending details,
    such as the method and path. However, in the event of a rate limit that applies
    to the route specifically, some fields will be populated such as `channel_id`
    and `guild_id` for "per-route" rate limitation.

    ---

    `channel_id` and `guild_id` are considered as top-level identifiers. On a given
    representation, these will be excluded. You will need to call these values
    separately in order to retrieve their values.
    """

    method: _RouteMethod = field(converter=_RouteMethod)
    """The route's method, e.g. `GET`."""
    path: str = field()
    """The path or URL to the route."""
    channel_id: str = field(default=None)
    """The channel ID associated with this route. This is for route-based rate limits."""
    guild_id: str = field(default=None)
    """The guild ID associated with this route. This is for route-based rate limits."""

    def __repr__(self) -> str:
        # We'll be associating our route as just the base URL for the API
        # and the path given. We don't need information for the method unless
        # we're in need of asserting it upon execution via. request.

        # TODO: check to see if the method is truly needed or not.

        return __api_url__.self.path

    def get_bucket(self, shared: NotNeeded[str] = MISSING) -> str:
        """
        Returns the bucket of the route. This will include top-level identifiers if present.

        Parameters
        ----------
        shared : `str`, optional
            The representation of another bucket as its own route, if present.
            When provided, a shared bucket relationship will be created.

        Returns
        -------
        `str`
            The current bucket of the route.

            If the bucket is not shared, the bucket will be based off of what Discord's
            currently provided to us as the route's information.
        """
        return (
            f"{self.channel_id}:{self.guild_id}:{self.path}"
            if shared is MISSING
            else f"{self.channel_id}:{self.guild_id}:{shared}"
        )


@define(slots=False)
class _Limit:
    """Represents a bucket that exists for a route."""

    event: Event = field(default=Event)
    """The asynchronous event associated to the bucket, used for blocking conditions."""
    reset_after: float = field(default=0.0)
    """The time remaining before the event may be reset. Defaults to `0.0`."""


class HTTPProtocol(Protocol):
    def __init__(self, token: str):
        ...

    async def request(self, route: _Route, payload: dict, retries: NotNeeded[int] = MISSING):
        ...


class HTTPClient(HTTPProtocol):
    """
    Represents a connection to Discord's REST API. The most common use case
    of the Discord API will be providing a service, or access to a platform
    through the OAuth2 API.

    Attributes
    ----------
    token : `str`
        The bot's token.
    _headers : `dict[str]`
        HTTP headers sent for authorisation purposes.
    _limits : `dict[_Route, str]`
        The buckets currently stored.
    _rate_limits : `dict[str, _Limit]`
        The rate limits currently stored.
    _global_rate_limit : `_Limit`
        The global rate limit state.
    """

    __slots__ = ("token", "_headers")
    token: str
    """The bot's token."""
    _headers: dict[str, str]
    """HTTP headers sent for authorisation purposes."""
    _buckets: dict[_Route, str]
    """The buckets currently stored."""
    _rate_limits: dict[str, _Limit]
    """The rate limits currently stored."""
    _global_rate_limit: _Limit
    """The global rate limit state.
"""

    def __init__(self, token: str):
        """
        Creates a new connection to the REST API.

        Parameters
        ----------
        token : `str`
            The bot's token to connect with.
        """
        self.token = token
        self._headers = {
            "Authorization": f"Bot {self.token}",
            "Content-Type": "application/json",
            "User-Agent": f"DiscordBot ({__repo_url__} {__version__}) "
            f"Python/{version_info[0]}.{version_info[1]} "
            f"httpx/{__http_version__}",
        }
        self._buckets = {}
        self._rate_limits = {}

    async def request(self, route: _Route, payload: dict, retries: NotNeeded[int] = MISSING):

        # TODO: Allow a reason field to be passed for audit log
        # purposes.

        if self._global_rate_limit.event.is_set() and self._global_rate_limit.reset_after != 0:
            logger.warning(
                f"There is still a global rate limit ongoing. Trying again in {self._global_rate_limit.reset_after}s."
            )
            await self._global_rate_limit.event.wait(self._global_rate_limit.reset_after)
            self._global_rate_limit.reset_after = 0.0
        elif self._global_rate_limit.reset_after == 0.0:
            self._global_rate_limit.event = Event()

        bucket_path = route.get_bucket(self._buckets.get(route))
        rate_limit = self._rate_limits.get(bucket_path)
        if rate_limit:
            if rate_limit.event.is_set() and rate_limit.reset_after != 0:
                logger.warning(
                    f"The current bucket {bucket_path} is still under a rate limit. Trying again in {rate_limit.reset_after}s."
                )
                await rate_limit.event.wait(rate_limit.reset_after)
                rate_limit.reset_after = 0.0
            elif rate_limit.reset_after == 0.0:
                rate_limit.event = Event()
        else:
            self._rate_limits[bucket_path] = _Limit()

        retry_attempts = 3 if retries is MISSING else retries
        for attempt in range(retry_attempts):
            try:
                resp: Response

                match route.method:
                    case _RouteMethod.GET:
                        resp = await get(route, params=QueryParams(**payload))
                    case _RouteMethod.POST:
                        resp = await post(route, json=payload)
                    case _RouteMethod.PUT:
                        resp = await put(route, json=payload)
                    case _RouteMethod.DELETE:
                        resp = await delete(route, params=QueryParams(**payload))

                json = resp.json()
                logger.debug(f"{route.method} {route}: {resp.status_code}")
                logger.debug(dumps(loads(json), indent=4, sort_keys=True))

                if isinstance(json, dict) and json.get("errors"):
                    raise HTTPException(json, severity=INFO)
                if resp.status_code == 429:
                    reset_after = resp.headers.get("X-RateLimit-Reset-After", 0.0)
                    if bool(resp.headers.get("X-RateLimit-Global")):
                        logger.warning(
                            f"A global rate limit has occured. Locking down future requests for {reset_after}s."
                        )
                        self._global_rate_limit.reset_after = reset_after
                        self._global_rate_limit.set()
                    else:
                        logger.warning(
                            f"A route-based rate limit has occured. Locking down future requests for {reset_after}s."
                        )
                        rate_limit.reset_after = reset_after
                        rate_limit.event.set()
                if resp.headers.get("X-RateLimit-Remaining", 0) == 0:
                    logger.warning(
                        f"We've reached the maximum number of requests possible. Locking down future requests for {reset_after}s."
                    )
                    await sleep_until(reset_after)

                return json
            except OSError as err:
                if attempt < 2 and err.errno in {54, 10054}:
                    await sleep_until(5)
            except Exception as err:
                logger.info(err)
