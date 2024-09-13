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

from app.db.models import Referral, Session, Promotion, Partner, Client
from app.repositories import ReferralRepository, PartnerRepository, ClientRepository
from app.services.sms import SmsService
from app.services.base import BaseService
from app.services.client import ClientService
from app.utils.decorators import session_required
from app.utils.sms_request import sms_request


class ReferralService(BaseService):
    async def _create(
            self,
            creator: str,
            code: str,
            client_id: int,
            return_model: bool = False,
    ):
        partner = await PartnerRepository().get_by_code(code)
        client = await ClientRepository().get_by_id(id_=client_id)
        referral = await ReferralRepository().create(
            partner=partner,
            client=client,
        )

        await self.create_action(
            model=referral,
            action='create',
            parameters={
                'creator': creator,
                'partner': partner.id,
                'client': client.id,
                'by_admin': True,
            }
        )

        if return_model:
            return referral

        return {'id': referral.id}

    @session_required(permissions=['referrals'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            code: str,
            client_id: int,
            return_model: bool = False,
    ):
        return await self._create(
            creator=f'session_{session.id}',
            code=code,
            client_id=client_id,
            return_model=return_model,
        )

    async def create_by_task(
            self,
            code: str,
            client_id: int,
    ):
        return await self._create(
            creator='sync_task',
            code=code,
            client_id=client_id,
            return_model=True,
        )

    @session_required(permissions=['referrals', 'partners'])
    async def add_by_admin(
            self,
            session: Session,
            code: str,
            name: str,
            phone: str,
    ):
        partner: Partner = await PartnerRepository.get_by_code(code=code, return_none=False)
        promotion: Promotion = partner.promotion
        client: Client = await ClientService().create_by_admin(
            session=session,
            fullname=name,
            phone=phone,
            return_model=True,
        )
        referral = await self.create_by_admin(
            session=session,
            code=code,
            client_id=client.id,
            return_model=True,
        )

        if promotion.sms_text_referral_bonus:
            message_referral_bonus = promotion.sms_text_referral_bonus.format(
                name=client.fullname,
                referral_bonus=int(promotion.referrer_bonus),
            )

            await sms_request(
                phone_number=client.phone,
                message=message_referral_bonus,
            )

            await SmsService().create(
                model='referral',
                model_id=referral.id,
                message=message_referral_bonus,
            )

        if promotion.sms_text_referrer_bonus:
            message_referrer_bonus = promotion.sms_text_referrer_bonus.format(
                fullname=partner.client.fullname,
                referrer_bonus=int(promotion.referrer_bonus),
            )

            await sms_request(
                phone_number=partner.client.phone,
                message=message_referrer_bonus,
            )

            await SmsService().create(
                model='partner',
                model_id=partner.id,
                message=message_referrer_bonus,
            )

        return {
            'partner': {
                'fullname': partner.client.fullname,
                'phone': partner.client.phone,
            },
            'promotion': {
                'referral_bonus': promotion.referral_bonus,
                'referrer_bonus': promotion.referrer_bonus,
            }
        }

    @session_required(permissions=['referrals'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        referral = await ReferralRepository().get_by_id(id_=id_)

        await ReferralRepository().delete(model=referral)

        await self.create_action(
            model=referral,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['referrals'], return_model=False)
    async def get_by_admin(
            self,
            id_: int,
    ):
        referral: Referral = await ReferralRepository().get_by_id(id_=id_)
        return {
            'referral': await self.generate_referral_dict(referral=referral)
        }

    @session_required(permissions=['referrals'], return_model=False, can_root=True)
    async def get_list_by_admin(self, partner_id: int):
        partner = await PartnerRepository().get_by_id(partner_id)
        return {
            'referrals': [
                await self.generate_referral_dict(referral=referral)
                for referral in await ReferralRepository().get_list_by_partner(partner=partner)
            ]
        }

    @staticmethod
    async def generate_referral_dict(referral: Referral):
        return {
            'id': referral.id,
            'partner': referral.partner.id,
            'client': referral.client.id,
            'created_at': referral.created_at,
        }
