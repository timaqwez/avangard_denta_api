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
from app.repositories import ClickRepository, PartnerRepository, LeadRepository
from app.db.models import Session, Lead
from app.utils.decorators import session_required
from app.utils.normalize_phone import normalize_phone_number


class LeadService(BaseService):
    async def create(
            self,
            code: str,
            name: str,
            phone: str,
    ):
        partner = await PartnerRepository().get_by_code(code=code, return_none=False)

        phone = normalize_phone_number(phone)

        lead = await LeadRepository().create(
            partner=partner,
            name=name,
            phone=phone,
        )

        await self.create_action(
            model=lead,
            action='create',
            parameters={
                'partner': partner.id,
                'name': name,
                'phone': phone,
            }
        )

        return {'id': lead.id}

    @session_required()
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            is_processed: bool,
    ):
        lead: Lead = await LeadRepository().get_by_id(id_=id_)

        await LeadRepository().update(
            model=lead,
            is_processed=is_processed,
        )

        await self.create_action(
            model=lead,
            action='update',
            parameters={
                'updater': f'session_{session.id}',
                'is_processed': is_processed,
            }
        )

        return {}

    @staticmethod
    async def generate_lead_dict(lead: Lead):
        return {
            'id': lead.id,
            'partner_id': lead.partner.id,
            'name': lead.name,
            'phone': lead.phone,
            'is_processed': lead.is_processed,
            'created_at': str(lead.created_at),
        }
