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

from app.db.models import Client
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class ClientRepository(BaseRepository):
    model = Client

    async def create(self, **kwargs):
        phone = kwargs.get('phone')
        try:
            client = Client.get(Client.phone == phone)
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Client',
                    'id_type': 'phone',
                    'id_value': phone,
                    'model_id': client.id,
                }
            )
        except DoesNotExist:
            return self.model.create(**kwargs)

    @staticmethod
    async def get_available_partners():
        return Client.select().where(Client.is_partner == True).execute()
