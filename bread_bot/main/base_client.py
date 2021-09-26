import json
import logging
import math
import time
from typing import Union

from httpx import AsyncClient, Response, Request, HTTPError, Headers
from httpx._client import UseClientDefault
from httpx._types import QueryParamTypes, HeaderTypes, URLTypes, AuthTypes, \
    RequestData, RequestContent

from bread_bot.utils.json_logger import EMPTY_VALUE
from bread_bot.utils.utils_schemas import RequestJsonLogSchema

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    """
    Базовый клиент для реализации HTTP запросов
    """

    async def request(
            self,
            method: str,
            url: URLTypes,
            headers: HeaderTypes = None,
            query_params: QueryParamTypes = None,
            auth: Union[AuthTypes, UseClientDefault] = None,
            data: Union[RequestContent, RequestData] = None,
    ) -> Response:
        """
        Сделать http запрос

        :param method: Метод (GET, POST, DELETE, PUT, HEAD, OPTIONS)
        :param url: URL адрес источника
        :param headers: Заголовки
        :param query_params: Параметры запроса
        :param auth: Объект BasicAuth
        :param data: Payload данные запроса в dict
        :return: Объект ответа httpx.Response
        """
        if isinstance(data, RequestData):
            data = json.dumps(data, ensure_ascii=False)
        start_time = time.time()
        exception_object = None
        request = Request(
            method=method,
            url=url,
            headers=headers,
            params=query_params,
            content=data,
        )
        try:
            async with AsyncClient(auth=auth) as async_client:
                response: Response = await async_client.send(
                    request=request,
                )
        except (ConnectionError, TimeoutError, HTTPError) as ex:
            exception_object = ex
            response = Response(status_code=000, content=b'', request=request)

        duration: int = math.ceil((time.time() - start_time) * 1000)
        await self.log(
            request=request,
            response=response,
            duration=duration,
            exception_object=exception_object,
        )
        return response

    @staticmethod
    async def _headers_json(headers: Headers) -> str:
        return json.dumps(dict(tuple(headers.multi_items())))

    async def log(self,
                  request: Request,
                  response: Response,
                  duration: int,
                  exception_object=None):
        """
        Логирование запроса и ответа

        :param request: Запрос
        :param response: Ответ
        :param duration: Время работы запроса
        :param exception_object: Ошибки
        :return:
        """
        response_content = response.content
        request_content = request.content
        request_json_fields = RequestJsonLogSchema(
            request_method=request.method,
            request_uri=str(request.url),
            request_body=request_content.decode(),
            request_referer=EMPTY_VALUE,
            request_path=request.url.path,
            request_direction='out',
            request_headers=await self._headers_json(request.headers),
            request_protocol='HTTP/1.1',
            request_host=request.url.host,
            request_content_type=EMPTY_VALUE,
            request_size=len(request_content),
            response_size=len(response_content),
            response_headers=await self._headers_json(response.headers),
            response_body=response_content.decode(),
            response_status_code=response.status_code,
            remote_ip=EMPTY_VALUE,
            remote_port=EMPTY_VALUE,
            duration=duration
        ).dict()
        message = f'{"Ошибка" if exception_object else "Ответ"} ' \
                  f'с кодом {response.status_code} ' \
                  f'на запрос {request.method} \"{str(request.url)}\", ' \
                  f'за {duration} мс'
        logger.info(
            message,
            extra={
                'request_json_fields': request_json_fields,
                'to_mask': True,
            },
            exc_info=exception_object,
        )
