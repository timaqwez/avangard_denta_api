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


from io import BufferedReader

from addict import Dict
from aiohttp import ClientSession, ContentTypeError, FormData
from furl import furl

from app.utils import ApiException


class RequestTypes:
    GET = 'get'
    POST = 'post'


async def _create_url(url, parameters: dict) -> str:
    f = furl(url=url)
    f.set(args=parameters)
    return f.url


async def _create_data(parameters, type_):
    parameters = parameters or {}

    json = {}
    url_parameters = {}
    data = FormData()

    have_data = False
    for pk, pv in parameters.items():
        if isinstance(pv, BufferedReader) or isinstance(pv, bytes):
            have_data = True
            data.add_field(name=pk, value=pv, filename='1.jpg', content_type='image/jpeg')
            continue

        url_parameters[pk] = pv

    if type_ == RequestTypes.POST and not have_data:
        json = url_parameters
        url_parameters = {}

    return json, url_parameters, data


async def request(
        url: str,
        type_: str = RequestTypes.POST,
        parameters: dict = None,
        response_key: str = None,
):
    json, url_parameters, data = await _create_data(
        parameters=parameters,
        type_=type_,
    )

    url = await _create_url(
        url=url,
        parameters=url_parameters,
    )

    async with ClientSession() as session:
        if type_ == RequestTypes.GET:
            response = await session.get(url=url)
        elif type_ == RequestTypes.POST and url_parameters:
            response = await session.post(url=url, data=data)
        elif type_ == RequestTypes.POST:
            response = await session.post(url=url, json=json)

        try:
            response_json = await response.json()
            response = Dict(**response_json)
        except ContentTypeError:
            return response

    if response.state == 'successful':
        if response_key:
            response = response.get(response_key)

        return response
    elif response.state == 'error':
        raise ApiException(message=response.error.message or response.message, kwargs=response.error.kwargs)
