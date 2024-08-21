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

from app.utils.exceptions import WrongTasksToken
from config import settings


def tasks_token_required():
    def inner(function):
        async def wrapper(*args, **kwargs):
            token = kwargs.get('token')
            if token != settings.tasks_token:
                raise WrongTasksToken()
            kwargs.pop('token')
            return await function(*args, **kwargs)
        return wrapper
    return inner
