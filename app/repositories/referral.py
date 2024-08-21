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

from app.db.models import Referral, Partner
from app.repositories.base import BaseRepository
from app.utils.exceptions import ModelAlreadyExist


class ReferralRepository(BaseRepository):
    model = Referral

    async def create(self, **kwargs):
        partner = kwargs.get('partner')
        client = kwargs.get('client')
        try:
            Referral.get(Referral.partner == partner, Referral.client == client)
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Referral',
                    'id_type': 'partner, client',
                    'id_value': [partner.id, client.id],
                }
            )
        except DoesNotExist:
            return self.model.create(**kwargs)

    @staticmethod
    async def get_list_by_partner(partner: Partner):
        return Referral.select().where(
            Referral.partner == partner
        ).execute()
