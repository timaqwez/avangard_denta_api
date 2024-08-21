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


from app.services.base import BaseService
from app.repositories import ClickRepository, PartnerRepository
from app.db.models import Session
from app.utils.decorators import session_required


class ClickService(BaseService):
    async def create(
            self,
            code: str,
            ip: str,
    ):
        partner = await PartnerRepository().get_by_code(code=code)

        click = await ClickRepository().create(
            partner=partner,
            ip=ip,
        )

        await self.create_action(
            model=click,
            action='create',
            parameters={
                'partner': partner.id,
            }
        )

        return {}

    @session_required(permissions=['promotions'])
    async def delete_by_admin(
            self,
            id_: int,
            session: Session,
    ):
        click = await ClickRepository().get_by_id(id_=id_)

        await ClickRepository().delete(model=click)

        await self.create_action(
            model=click,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['promotions'], return_model=False, can_root=True)
    async def get_list_by_admin(self, partner_id: int):
        partner = await PartnerRepository().get_by_id(partner_id)
        return {
            'clicks': [
                {
                    'id': click.id,
                    'partner': click.partner.id,
                    'ip': click.ip,
                } for click in await partner.clicks
            ]
        }
