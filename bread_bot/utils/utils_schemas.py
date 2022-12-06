from typing import Union

from pydantic import BaseModel, Field


class BaseJsonLogSchema(BaseModel):
    """
    Схема основного тела лога в формате JSON
    """

    thread: Union[int, str]
    level: int
    level_name: str
    message: str
    source: str
    timestamp: str = Field(..., alias="@timestamp")
    app_name: str
    app_version: str
    app_env: str
    duration: int
    exceptions: Union[list[str], str] = None
    trace_id: str = None
    span_id: str = None
    parent_id: str = None

    class Config:
        allow_population_by_field_name = True


class RequestJsonLogSchema(BaseModel):
    """
    Схема части запросов-ответов лога в формате JSON
    """

    request_uri: str
    request_referer: str
    request_protocol: str
    request_method: str
    request_path: str
    request_host: str
    request_size: int
    request_content_type: str
    request_headers: str
    request_body: Union[str, dict, list]
    request_direction: str
    remote_ip: str
    remote_port: str
    response_status_code: int
    response_size: int
    response_headers: str
    response_body: Union[str, dict, list]
    duration: int
