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

from json import loads
from types import SimpleNamespace

from pydantic import Json

from app.db.models import Referral, Session, Client, Partner, Promotion
from app.repositories import ClientRepository
from app.services.base import BaseService
from app.utils.decorators import session_required, tasks_token_required
from app.utils.exceptions import ModelAlreadyExist
from app.utils.normalize_phone import normalize_phone_number
from app.utils.sms_request import sms_request


class ClientService(BaseService):
    @session_required(permissions=['clients'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            fullname: str,
            phone: str,
            email: str = None,
            is_partner: bool = False,
            return_model: bool = False,
    ):
        phone = normalize_phone_number(phone)

        client = await ClientRepository().create(
            fullname=fullname,
            email=email,
            is_partner=is_partner,
            phone=phone,
        )

        await self.create_action(
            model=client,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'fullname': fullname,
                'email': email,
                'phone': phone,
                'is_partner': is_partner,
                'by_admin': True,
            }
        )

        if return_model:
            return client

        return {'id': client.id}

    @session_required(permissions=['clients'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        client = await ClientRepository().get_by_id(id_=id_)

        await ClientRepository().delete(model=client)

        await self.create_action(
            model=client,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['clients'], return_model=False)
    async def get_by_admin(
            self,
            id_: int,
    ):
        client: Client = await ClientRepository().get_by_id(id_=id_)
        return {
            'client': await self.generate_client_dict(client=client)
        }

    @session_required(permissions=['clients'], return_model=False, can_root=True)
    async def get_list_by_admin(self):
        return {
            'clients': [
                await self.generate_client_dict(client=client)
                for client in await ClientRepository().get_list()
            ]
        }

    @session_required(permissions=['partners'], return_model=False, can_root=True)
    async def get_list_partners_by_admin(self):
        return {
            'partners': [
                await self.generate_client_dict(partner)
                for partner in await ClientRepository().get_available_partners()
            ]
        }

    # @tasks_token_required()
    # async def sync_1c(self, data: Json):
    #     clients = loads(data, object_hook=lambda d: SimpleNamespace(**d))
    #     bonuses = []
    #     for client in clients:
    #         client_inst = await self.get_or_create_by_task(
    #             user_id=client.user_id,
    #             fullname=client.fullname,
    #             email=client.email,
    #             phone=client.phone,
    #             is_partner=client.is_partner,
    #         )
    #         if client.bonus_code:
    #             try:
    #                 referral_inst: Referral = await ReferralService().create_by_task(
    #                     code=client.bonus_code,
    #                     client_id=client_inst.id,
    #                 )
    #                 partner: Partner = referral_inst.partner
    #                 promotion: Promotion = partner.promotion
    #
    #                 await sms_request(
    #                     phone_number=partner.client.phone,
    #                     message=promotion.sms_text_for_referral.format(
    #                         fullname=client.fullname,
    #                         referrer_bonus=promotion.referrer_bonus,
    #                     )
    #                 )
    #                 await sms_request(
    #                     phone_number=client.phone,
    #                     message=promotion.sms_text_for_referral.format(
    #                         name=client.fullname,
    #                         referral_bonus=promotion.referral_bonus,
    #                     )
    #                 )
    #
    #                 bonuses.append(
    #                     {
    #                         'user_id': partner.client.id,
    #                         'operation': 'add',
    #                         'amount': promotion.referrer_bonus,
    #                     }
    #                 )
    #                 bonuses.append(
    #                     {
    #                         'user_id': client_inst.id,
    #                         'operation': 'add',
    #                         'amount': promotion.referral_bonus,
    #                     }
    #                 )
    #             except ModelAlreadyExist:
    #                 pass
    #     return bonuses

    @staticmethod
    async def generate_client_dict(client: Client):
        return {
            'id': client.id,
            'fullname': client.fullname,
            'email': client.email,
            'phone': client.phone,
            'is_partner': client.is_partner,
        }
