import logging
import logging.config
from typing import Optional, Any

import yaml
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.middleware.authentication import AuthenticationMiddleware
from utilswaves.common import register_exception_handler
from utilswaves.dependencies import get_correlation_id
from utilswaves.lifespan_manager import LifespanManager
from utilswaves.middlewares import HermesAlertMiddleware, AccessLoggerMiddleware
from utilswaves.middlewares.access_monitor_middleware import AccessMonitorMiddleware
from utilswaves.schema import NAMESPACE

from api import api
from core.config import Settings, BASEDIR
# from app.core.client.redis import redis_client
from app.core.middleware.auth import AuthBackend, on_auth_error

logger = logging.getLogger(__name__)

_app: Optional[FastAPI] = None


def create_app(app_settings: Settings, lifespan_manager: LifespanManager = None, **kwargs):
    global _app
    if _app:
        return _app

    initial_logger(app_settings)

    logger.info("Create Application ...")
    logger.info(f"NAMESPACE: {app_settings.namespace}")
    logger.debug(f"Settings: {app_settings}")

    lifespan_manager = lifespan_manager or LifespanManager()
    app_params = setting_params(app_settings, kwargs)
    app = FastAPI(**app_params, lifespan=lifespan_manager, default_response_class=ORJSONResponse)

    # # 注册中间件
    register_middleware(app, app_settings)

    # 注册异常处理器
    logger.info("Register Exception Handler")
    register_exception_handler(app)

    # 注册外部服务
    # register_client(app_settings)

    # registry routers
    register_router(app)

    _app = app
    return _app


def initial_logger(app_settings):
    with open(BASEDIR.joinpath("configs/log_config.yaml")) as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
    if app_settings.app.debug:
        logging.getLogger("root").setLevel(logging.DEBUG)


def setting_params(app_settings: Settings, params: Optional[dict]) -> dict[str, Any]:
    params = params or {}
    params.setdefault("title", app_settings.app_name)
    params.setdefault("version", app_settings.version)
    description = f"""
NAMESPACE: **{app_settings.namespace.upper()}**
"""
    logger.info(f"setting_params {app_settings=}")
    params.setdefault("description", description)
    match app_settings.namespace:
        case NAMESPACE.LOCAL:
            params.setdefault("debug", app_settings.app.debug)
        case NAMESPACE.DEV:
            logger.info("setting_params root")
            params.setdefault("root_path", "/dev/kuka/")
        case NAMESPACE.PROD:
            params.setdefault("docs_url", None)
            params.setdefault("redoc_url", None)
            params.setdefault("openapi_url", None)

    return params


def register_middleware(app: FastAPI, app_settings: Settings):

    app.add_middleware(
        AuthenticationMiddleware,
        backend=AuthBackend(exclude=["POST-/login", "GET-/docs", "GET-/openapi.json", "GET-/metrics"]),
        on_error=on_auth_error,
    )

    logger.info("Register HermesAlert Middleware")
    if app_settings.namespace != NAMESPACE.LOCAL:
        logger.info("Register HermesAlert Middleware")
        app.add_middleware(
            HermesAlertMiddleware,
            app_name=app_settings.app_name,
            namespace=app_settings.namespace,
            **app_settings.hermes.model_dump(),
        )

    # generate request_id
    logger.info("Register CorrelationId Middleware")
    app.add_middleware(CorrelationIdMiddleware)

    logger.info("Register Access Middleware")
    # start with uvicorn, uvicorn.access format cant change
    _logger = (
        logging.getLogger("uvicorn.access") if app_settings.namespace not in [NAMESPACE.LOCAL, NAMESPACE.TEST] else None
    )
    app.add_middleware(AccessLoggerMiddleware, logger=_logger, request_id_factory=get_correlation_id)

    app.add_middleware(AccessMonitorMiddleware)

    logger.info("Register CORS Middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许的域名列表
        allow_credentials=True,  # 允许在跨域请求中使用凭证（如Cookie）
        allow_methods=["*"],  # 允许的请求方法列表，这里使用通配符表示支持所有方法
        allow_headers=["*"],  # 允许的请求头列表，这里使用通配符表示支持所有头部字段
        # Indicate which headers can be exposed as part of the response to a browser
        expose_headers=["X-Request-Id", "X-Model-Type"],
    )


# def register_client(app_settings: Settings):
#     redis_client.configure(
#         app_settings.redis.url,
#         prefix=f"{app_settings.app_name}:{app_settings.namespace}",
#     )


def register_databases(lifespan_manager, app_settings: Settings):
    pass


def register_router(app):
    app.include_router(api.router)
