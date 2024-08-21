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
import base64
import binascii
from base64 import b64decode
from random import choice

from app.services.base import BaseService
from app.repositories import PartnerRepository, PromotionRepository, ClientRepository
from app.db.models import Partner, Session, Client, Promotion
from app.utils.crypto import generate_base64_string
from app.utils.decorators import session_required
from app.utils.exceptions.main import VariableDoesNotMatchFormat, ModelDoesNotExist
from app.utils.sms_request import sms_request
from config import settings


class PartnerService(BaseService):
    async def _create(
            self,
            creator: str,
            promotion_id: int,
            client_id: int,
            return_model: bool = False,
    ):
        promotion: Promotion = await PromotionRepository().get_by_id(id_=promotion_id)
        client: Client = await ClientRepository().get_by_id(id_=client_id)

        while True:
            code = self.generate_referral_code()
            try:
                await PartnerRepository().get_by_code(code, return_none=False)
            except ModelDoesNotExist:
                break

        partner = await PartnerRepository().create(
            code=code,
            promotion=promotion,
            client=client,
        )

        await sms_request(
            phone_number=client.phone,
            message=promotion.sms_text_partner_create.format(
                fullname=' '.join(filter(None, [client.lastname, client.firstname, client.surname])),
                link=f'{settings.referral_site_url}/{await generate_base64_string(code)}',
                referrer_bonus=promotion.referrer_bonus,
                referral_bonus=promotion.referral_bonus,
            )
        )

        await sms_request(
            phone_number=client.phone,
            message=promotion.sms_text_for_referral.format(
                link=f'{settings.referral_site_url}/{await generate_base64_string(code)}',
                referral_bonus=promotion.referral_bonus,
            )
        )

        await self.create_action(
            model=partner,
            action='create',
            parameters={
                'creator': creator,
                'client': client_id,
                'promotion': promotion_id,
                'by_admin': True,
            }
        )

        if return_model:
            return partner

        return {'id': partner.id}

    @session_required(permissions=['partners'])
    async def create_by_admin(
            self,
            session: Session,
            promotion_id: int,
            client_id: int,
    ):
        return await self._create(
            promotion_id=promotion_id,
            client_id=client_id,
            creator=f'session_{session.id}',
        )

    async def create_by_task(
            self,
            promotion_id: int,
            client_id: int,
    ):
        return await self._create(
            promotion_id=promotion_id,
            client_id=client_id,
            creator=f'sync_task',
            return_model=True,
        )

    async def _delete(
            self,
            id_: int,
            session: Session = None,
    ):
        partner = await PartnerRepository().get_by_id(id_=id_)

        await PartnerRepository().delete(model=partner)

        await self.create_action(
            model=partner,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}' if session else 'task',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['partners'])
    async def delete_by_admin(
            self,
            id_: int,
            session: Session,
    ):
        return await self._delete(
            id_=id_,
            session=session,
        )

    @session_required(permissions=['partners'], return_model=False)
    async def get_by_admin(
            self,
            code: str,
    ):
        partner: Partner = await PartnerRepository().get_by_code(code)
        return {
            'partner': await self.generate_partner_dict(partner)
        }

    @session_required(permissions=['partners'], return_model=False, can_root=True)
    async def get_list_by_admin(self, promotion_id: int):
        promotion = await PromotionRepository().get_by_id(id_=promotion_id)
        return {
            'partners': [
                await self.generate_partner_dict(partner)
                for partner in await PartnerRepository().get_list_by_promotion(promotion)
            ]
        }

    @session_required(permissions=['partners'], return_model=False, can_root=True)
    async def get_list_available_by_admin(self, promotion_id: int):
        promotion = await PromotionRepository().get_by_id(id_=promotion_id)
        return {
            'partners': [
                await self.generate_partner_dict(partner)
                for partner in await PartnerRepository().get_list_by_promotion(promotion)
            ]
        }

    @staticmethod
    async def generate_partner_dict(partner: Partner):
        return {
            'id': partner.id,
            'code': partner.code,
            'fullname': f'{partner.client.lastname or ""} {partner.client.firstname or ""} {partner.client.surname or ""}',
            'email': partner.client.email,
            'phone': partner.client.phone,
            'referrals': len(partner.referrals),
            'clicks': len(partner.clicks),
            'leads': len(partner.leads),
            'client': partner.client.id,
        }

    @staticmethod
    async def check_code(base64code: str):
        try:
            code = base64.b64decode(base64code).decode()
        except Exception as e:
            raise VariableDoesNotMatchFormat(
                kwargs={
                    'variable': 'code'
                }
            )
        await PartnerRepository().get_by_code(code, return_none=False)
        return {
            'code': code
        }

    @staticmethod
    def generate_referral_code():
        russian_letters = 'АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЩЭЮЯ'
        letters = ''.join(choice(russian_letters) for _ in range(2))
        digits = ''.join(choice('0123456789') for _ in range(4))
        referral_code = letters + digits
        return referral_code
