#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import logging

from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.db import create_models
from app.utils.validation_error import validation_error
from app.utils.client import init
from app.utils.middleware import Middleware
from app.routers import routers


app = FastAPI(
    title='Avangard Admin API',
    version='0.1',
    dependencies=[Depends(init)],
    exception_handlers={RequestValidationError: validation_error},
)

# noinspection PyTypeChecker
app.add_middleware(
    middleware_class=BaseHTTPMiddleware,
    dispatch=Middleware(),
)
[app.include_router(router) for router in routers]

origins = [
    "http://localhost",
    "http://localhost:1011",
    "http://127.1.0.0:1011",
    "http://127.1.0.0",
]

# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_app():
    logging.basicConfig(level=logging.DEBUG)
    logging.info(msg='Application starting...')

    create_models()
    return app
