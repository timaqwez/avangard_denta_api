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
from app.services import ReferralService
from app.services.base import BaseService
from app.utils.decorators import session_required, tasks_token_required
from app.utils.exceptions import ModelAlreadyExist
from app.utils.sms_request import sms_request


class ClientService(BaseService):
    @session_required(permissions=['clients'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            user_id: int,
            firstname: str,
            email: str,
            phone: str,
            lastname: str = None,
            surname: str = None,
            is_partner: bool = None,
    ):
        client = await ClientRepository().create(
            user_id=user_id,
            firstname=firstname,
            email=email,
            lastname=lastname,
            surname=surname,
            is_partner=is_partner,
            phone=phone,
        )

        action_parameters = {
            'creator': f'session_{session.id}',
            'user': user_id,
            'firstname': firstname,
            'email': email,
            'phone': phone,
            'by_admin': True,
        }
        if lastname:
            action_parameters['lastname'] = lastname
        if surname:
            action_parameters['surname'] = surname

        await self.create_action(
            model=client,
            action='create',
            parameters=action_parameters,
        )

        return {'id': client.id}

    async def get_or_create_by_task(
            self,
            user_id: int,
            firstname: str,
            email: str,
            phone: str,
            lastname: str = None,
            surname: str = None,
            is_partner: bool = None,
    ):
        client = await ClientRepository().get_or_create(
            user_id=user_id,
            firstname=firstname,
            email=email,
            phone=phone,
            lastname=lastname,
            surname=surname,
            is_partner=is_partner,
        )

        update_parameters = {}

        if client.firstname != firstname:
            update_parameters['firstname'] = firstname
        if client.email != email:
            update_parameters['email'] = email
        if client.phone != phone:
            update_parameters['phone'] = phone
        if lastname is not None and client.lastname != lastname:
            update_parameters['lastname'] = lastname
        if surname is not None and client.surname != surname:
            update_parameters['surname'] = surname
        if is_partner is not None and client.is_partner != is_partner:
            update_parameters['is_partner'] = is_partner

        if len(update_parameters.keys()) > 0:
            update_parameters['client'] = client
            await self.update_by_task(**update_parameters)

        action_parameters = {
            'creator': 'sync_task',
            'user': user_id,
            'firstname': firstname,
            'email': email,
            'phone': phone,
            'by_admin': True,
        }
        if lastname:
            action_parameters['lastname'] = lastname
        if surname:
            action_parameters['surname'] = surname

        await self.create_action(
            model=client,
            action='create',
            parameters=action_parameters,
        )

        return client

    async def update_by_task(
            self,
            client: Client,
            firstname: str = None,
            email: str = None,
            phone: str = None,
            lastname: str = None,
            surname: str = None,
            is_partner: bool = None,
    ):
        action_parameters = {
            'creator': 'sync_task',
        }
        if firstname:
            action_parameters['firstname'] = firstname
        if email:
            action_parameters['email'] = email
        if phone:
            action_parameters['phone'] = phone
        if lastname:
            action_parameters['lastname'] = lastname
        if surname:
            action_parameters['surname'] = surname
        if is_partner:
            action_parameters['is_partner'] = is_partner

        await ClientRepository().update(
            model=client,
            firstname=firstname,
            email=email,
            phone=phone,
            lastname=lastname,
            surname=surname,
            is_partner=is_partner,
        )

        await self.create_action(
            model=client,
            action='update',
            parameters=action_parameters,
        )

        return {}

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

    @tasks_token_required()
    async def sync_1c(self, data: Json):
        clients = loads(data, object_hook=lambda d: SimpleNamespace(**d))
        bonuses = []
        for client in clients:
            client_inst = await self.get_or_create_by_task(
                user_id=client.user_id,
                firstname=client.firstname,
                lastname=client.lastname,
                surname=client.surname,
                email=client.email,
                phone=client.phone,
                is_partner=client.is_partner,
            )
            if client.bonus_code:
                try:
                    referral_inst: Referral = await ReferralService().create_by_task(
                        code=client.bonus_code,
                        client_id=client_inst.id,
                    )
                    partner: Partner = referral_inst.partner
                    promotion: Promotion = partner.promotion

                    await sms_request(
                        phone_number=partner.client.phone,
                        message=promotion.sms_text_for_referral.format(
                            fullname=' '.join(filter(None, [client.lastname, client.firstname, client.surname])),
                            referrer_bonus=promotion.referrer_bonus,
                        )
                    )
                    await sms_request(
                        phone_number=client.phone,
                        message=promotion.sms_text_for_referral.format(
                            name=client.firstname,
                            referral_bonus=promotion.referral_bonus,
                        )
                    )

                    bonuses.append(
                        {
                            'user_id': partner.client.id,
                            'operation': 'add',
                            'amount': promotion.referrer_bonus,
                        }
                    )
                    bonuses.append(
                        {
                            'user_id': client_inst.id,
                            'operation': 'add',
                            'amount': promotion.referral_bonus,
                        }
                    )
                except ModelAlreadyExist:
                    pass
        return bonuses

    @staticmethod
    async def generate_client_dict(client: Client):
        return {
            'id': client.id,
            'user_id': client.user_id,
            'fullname': f'{client.lastname or ""} {client.firstname or ""} {client.surname or ""}',
            'email': client.email,
            'phone': client.phone,
            'is_partner': client.is_partner,
        }
