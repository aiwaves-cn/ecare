import logging

import asgi_correlation_id
from httpx import AsyncClient, HTTPStatusError


logger = logging.getLogger(__name__)

_default_format = "[%(asctime)s] [%(levelname)7s] [%(correlation_id)s] [%(funcName)s - %(module)s:%(lineno)d] %(message)s"


def init_logging(_format=_default_format, set_request_id: bool = True, formatter_cls=logging.Formatter, debug=False):
    formatter = formatter_cls(_format)

    handlers = []
    if set_request_id:
        request_handler = logging.StreamHandler()
        request_handler.setFormatter(formatter)
        request_handler.addFilter(asgi_correlation_id.CorrelationIdFilter(uuid_length=32, default_value="-"))
        handlers.append(request_handler)

    logging.basicConfig(
        level=logging.INFO if not debug else logging.DEBUG,
        handlers=handlers,
        force=True
    )