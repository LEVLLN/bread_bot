import http
import json
import logging
import math
import time

from fastapi import Request, Response
from opencensus.common.transports import sync
from opencensus.trace import (
    attributes_helper,
    execution_context,
    samplers,
)
from opencensus.trace import span as span_module
from opencensus.trace import tracer as tracer_module
from opencensus.trace import utils
from opencensus.trace.base_exporter import Exporter
from opencensus.trace.propagation import trace_context_http_header_format
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp, Message

from bread_bot.main.settings import PORT
from bread_bot.utils.json_logger import EMPTY_VALUE
from bread_bot.utils.utils_schemas import RequestJsonLogSchema

HTTP_HOST = attributes_helper.COMMON_ATTRIBUTES['HTTP_HOST']
HTTP_METHOD = attributes_helper.COMMON_ATTRIBUTES['HTTP_METHOD']
HTTP_PATH = attributes_helper.COMMON_ATTRIBUTES['HTTP_PATH']
HTTP_ROUTE = attributes_helper.COMMON_ATTRIBUTES['HTTP_ROUTE']
HTTP_URL = attributes_helper.COMMON_ATTRIBUTES['HTTP_URL']
HTTP_STATUS_CODE = attributes_helper.COMMON_ATTRIBUTES['HTTP_STATUS_CODE']

logger = logging.getLogger(__name__)


class DefaultExporter(Exporter):
    """Export the spans by printing them.

    :type transport: :class:`type`
    :param transport: Class for creating new transport objects. It should
                      extend from the base_exporter :class:`.Transport` type
                      and implement :meth:`.Transport.export`. Defaults to
                      :class:`.SyncTransport`. The other option is
                      :class:`.AsyncTransport`.
    """

    def __init__(self, transport=sync.SyncTransport):
        self.transport = transport(self)

    def emit(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to emit
        """
        pass

    def export(self, span_datas):
        """
        :type span_datas: list of :class:
            `~opencensus.trace.span_data.SpanData`
        :param list of opencensus.trace.span_data.SpanData span_datas:
            SpanData tuples to export
        """
        self.transport.export(span_datas)


class LoggingMiddleware:
    """
    Middleware для обработки запросов и ответов с целью журналирования
    """
    @staticmethod
    async def get_protocol(request: Request) -> str:
        protocol = str(request.scope.get('type', ''))
        http_version = str(request.scope.get('http_version', ''))
        if protocol.lower() == 'http' and http_version:
            return f'{protocol.upper()}/{http_version}'
        return EMPTY_VALUE

    @staticmethod
    async def set_body(request: Request, body: bytes) -> None:
        async def receive() -> Message:
            return {'type': 'http.request', 'body': body}

        request._receive = receive

    async def get_body(self, request: Request) -> bytes:
        body = await request.body()
        await self.set_body(request, body)
        return body

    async def __call__(
            self, request: Request, call_next: RequestResponseEndpoint,
            *args, **kwargs
    ):
        start_time = time.time()
        exception_object = None
        # Request Side
        try:
            raw_request_body = await request.body()
            await self.set_body(request, raw_request_body)
            raw_request_body = await self.get_body(request)
            request_body = raw_request_body.decode()
        except AttributeError:
            request_body = EMPTY_VALUE

        try:
            if request_body != EMPTY_VALUE:
                request_body = json.loads(request_body)
        except json.decoder.JSONDecodeError:
            pass

        server: tuple = request.get('server', ('localhost', PORT))
        request_headers: dict = dict(request.headers.items())
        # Response Side
        try:
            response = await call_next(request)
        except Exception as ex:
            response_body = bytes(
                http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase.encode()
            )
            response = Response(
                content=response_body,
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR.real,
            )
            exception_object = ex
            response_headers = {}
        else:
            response_headers = dict(response.headers.items())
            response_body = b''
            async for chunk in response.body_iterator:
                response_body += chunk
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        duration: int = math.ceil((time.time() - start_time) * 1000)

        try:
            response_body = json.loads(response_body)
        except json.decoder.JSONDecodeError:
            response_body = response_body.decode()

        request_json_fields = RequestJsonLogSchema(
            request_uri=str(request.url),
            request_referer=request_headers.get('referer', EMPTY_VALUE),
            request_protocol=await self.get_protocol(request),
            request_method=request.method,
            request_path=request.url.path,
            request_host=f'{server[0]}:{server[1]}',
            request_size=int(request_headers.get('content-length', 0)),
            request_content_type=request_headers.get(
                'content-type', EMPTY_VALUE),
            request_headers=json.dumps(request_headers, ensure_ascii=False),
            request_body=request_body,
            request_direction='in',
            remote_ip=request.client[0],
            remote_port=request.client[1],
            response_status_code=response.status_code,
            response_size=int(response_headers.get('content-length', 0)),
            response_headers=json.dumps(response_headers, ensure_ascii=False),
            response_body=response_body,
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
        return response


class OpenCensusFastAPIMiddleware:
    """
    Middleware для реализации телеметрии для веб-запросов
    """

    def __init__(
            self,
            app: ASGIApp,
            excludelist_paths=None,
            excludelist_hostnames=None,
            sampler=None,
            exporter=None,
            propagator=None,
    ) -> None:
        self.app = app
        self.excludelist_paths = excludelist_paths
        self.excludelist_hostnames = excludelist_hostnames
        self.sampler = sampler or samplers.AlwaysOnSampler()
        self.exporter = exporter or DefaultExporter()
        self.propagator = (
                propagator
                or trace_context_http_header_format.TraceContextPropagator()
        )

    async def __call__(self, request: Request, call_next):

        # Do not trace if the url is in the exclude list
        if utils.disable_tracing_url(
                url=str(request.url),
                excludelist_paths=self.excludelist_paths
        ):
            return await call_next(request)

        try:
            span_context = self.propagator.from_headers(request.headers)

            fastapi_tracer = tracer_module.Tracer(
                span_context=span_context,
                sampler=self.sampler,
                exporter=self.exporter,
                propagator=self.propagator,
            )
        except Exception as ex:  # pragma: NO COVER
            logger.error("Failed to trace request", exc_info=ex)
            return await call_next(request)

        try:
            span = fastapi_tracer.start_span()
            span.span_kind = span_module.SpanKind.SERVER
            span.name = "[{}]{}".format(request.method, request.url)
            fastapi_tracer.add_attribute_to_current_span(
                HTTP_HOST,
                request.url.hostname,
            )
            fastapi_tracer.add_attribute_to_current_span(
                HTTP_METHOD,
                request.method,
            )
            fastapi_tracer.add_attribute_to_current_span(
                HTTP_PATH,
                request.url.path,
            )
            fastapi_tracer.add_attribute_to_current_span(
                HTTP_URL,
                str(request.url),
            )
            execution_context.set_opencensus_attr(
                'excludelist_hostnames', self.excludelist_hostnames
            )
        except Exception as ex:
            logger.error('Failed to trace request', exc_info=ex)

        response = await call_next(request)
        try:
            fastapi_tracer.add_attribute_to_current_span(
                HTTP_STATUS_CODE,
                response.status_code,
            )
        except Exception as ex:
            logger.error('Failed to trace response', exc_info=ex)
        finally:
            fastapi_tracer.end_span()
            return response
