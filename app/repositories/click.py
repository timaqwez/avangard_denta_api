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
from peewee import DoesNotExist

from app.db.models import Click, Partner
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class ClickRepository(BaseRepository):
    model = Click

    async def create(self, **kwargs):
        ip = kwargs.get('ip')
        try:
            Click.get(Click.ip == ip)
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Click',
                    'id_type': 'ip',
                    'id_value': ip,
                }
            )
        except DoesNotExist:
            return self.model.create(**kwargs)
