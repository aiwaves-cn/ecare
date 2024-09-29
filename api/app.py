#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2024/5/21 16:56
# @File    : app.py
# @Software: PyCharm
import os

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware

from api.chat import router
from api.utils import init_logging

init_logging(debug=os.environ.get("DEBUG") == "true")

app = FastAPI(
    title="e_care",
    version="0.0.1",
    description="",
    docs_url="/mydocs",  
    redoc_url="/myredoc",
    openapi_url="/openapi.json" 
)

# def custom_swagger_ui_html(*, request):
#  openapi_url = app.openapi_url
#  swagger_url = openapi_url.replace("/openapi.json", "/swagger")
#  return get_swagger_ui_html(
#      openapi_url=openapi_url,
#      title=app.title + " - Swagger UI",
#      oauth2_redirect_url=swagger_url + "/oauth2-redirect.html",
#      swagger_js_url="/static/swagger-ui-bundle.js",
#      swagger_css_url="/static/swagger-ui.css",
#  )

# app.openapi = get_openapi(title="My API")

# @app.get("/swagger", include_in_schema=False)
# async def swagger_ui_html(request: Request):
#  return custom_swagger_ui_html(request=request)

# app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的域名列表
    allow_credentials=True,  # 允许在跨域请求中使用凭证（如Cookie）
    allow_methods=["*"],  # 允许的请求方法列表，这里使用通配符表示支持所有方法
    allow_headers=["*"],  # 允许的请求头列表，这里使用通配符表示支持所有头部字段
    # Indicate which headers can be exposed as part of the response to a browser
    expose_headers=["X-Request-Id"],
)

app.include_router(router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app)



