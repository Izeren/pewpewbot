import aiohttp
import json
import logging
from dataclasses import dataclass

from marshmallow import EXCLUDE

from pewpewbot.models import CodeSchema, CodeVerdict, Status, StatusSchema, TokenSchema
from pewpewbot.errors import AuthenticationError, wrap_errors, ValidationError

DEFAULT_ENDPOINT = 'http://classic.dzzzr.ru'
DEFAULT_CITY = 'moscow'


class Urls:
    def __init__(self, endpoint=DEFAULT_ENDPOINT, city=DEFAULT_CITY):
        base = f'{endpoint}/{city}'
        self.log_in = f'{base}/API/login.php'
        self.status = f'{base}/go/'
        self.post_code = f'{base}/go/'


@dataclass
class ClientConfig:
    total_timeout: float
    max_concurrent_connections: int


DEFAULT_URLS = Urls()
DEFAULT_CONFIG = ClientConfig(total_timeout=20, max_concurrent_connections=5)


class Client:
    def __init__(self, urls: Urls = DEFAULT_URLS, config: ClientConfig = DEFAULT_CONFIG):
        self._urls = urls
        self._client = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=config.max_concurrent_connections),
            timeout=aiohttp.ClientTimeout(total=config.total_timeout),
            raise_for_status=True)
        self._entered = False
        self._token = None
        self.logger = logging.getLogger(Client.__name__)

    @property
    def token(self):
        if self._token is None:
            raise AuthenticationError('Not logged in')
        return self._token

    async def __aenter__(self):
        await self._client.__aenter__()
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._entered = False
        await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def _request(self, method, url, **kwargs):
        # if not self._entered:
        #     raise TypeError(
        #         'The Client object should be used as an asynchronous context manager ("async with Client(...)")')
        async with self._client.request(method, url, **kwargs) as resp:
            body = await resp.read()
            pos = body.find(b'{')
            if pos == -1:
                raise ValidationError(body)
            body = body[pos:].decode('utf-8')
            return json.loads(body)

    @wrap_errors
    async def log_in(self, login, password):
        resp = await self._request(
            'get', self._urls.log_in, params=dict(login=login, password=password),
            auth=aiohttp.BasicAuth(login=login, password=password))
        self.logger.info("Server response on log in request {}".format(resp))
        self._token = TokenSchema(partial=True, unknown=EXCLUDE).load(resp)

    @wrap_errors
    async def status(self) -> Status:
        resp = await self._request(
            'get', self._urls.status, params=dict(
                s=self.token,
                api='true'))
        self.logger.info("Server response on game status request {}".format(resp))
        return StatusSchema(partial=True, unknown=EXCLUDE).load(resp)

    @wrap_errors
    async def post_code(self, code: str) -> CodeVerdict:
        resp = await self._request(
            'post', self._urls.status + '?api=true', data=dict(
                s=self.token,
                action='entcod',
                cod=code))
        self.logger.info("Server response on post code request {}".format(resp))
        return CodeSchema(partial=True, unknown=EXCLUDE).load(resp)
