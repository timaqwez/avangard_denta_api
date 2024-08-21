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

from app.db.models import Partner, Promotion
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist, ModelDoesNotExist


class PartnerRepository(BaseRepository):
    model = Partner

    async def create(self, **kwargs):
        client = kwargs.get('client')
        promotion = kwargs.get('promotion')
        try:
            Partner.get(Partner.client == client, Partner.promotion == promotion, Partner.is_deleted == 0)
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Partner',
                    'id_type': 'client_id',
                    'id_value': client.id,
                }
            )
        except DoesNotExist:
            return self.model.create(**kwargs)

    @staticmethod
    async def get_by_code(code: str, return_none: bool = True):
        if return_none:
            return Partner.get_or_none(
                Partner.code == code,
                Partner.is_deleted == False,
            )
        else:
            try:
                return Partner.get(
                    Partner.code == code,
                    Partner.is_deleted == False,
                )
            except DoesNotExist:
                raise ModelDoesNotExist(
                    kwargs={
                        'model': 'Partner',
                        'id_type': 'code',
                        'id_value': code,
                    },
                )

    @staticmethod
    async def get_list_by_promotion(promotion: Promotion):
        return Partner.select().where(
            Partner.promotion == promotion,
            Partner.is_deleted == False,
        ).execute()


