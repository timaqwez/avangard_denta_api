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

from app.db.models import Account, Session
from app.repositories import AccountRepository, AccountRoleRepository
from app.services.account_role import AccountRoleService
from app.services.base import BaseService
from app.utils.crypto import create_salt, create_hash_by_string_and_salt
from app.utils.decorators import session_required
from app.utils.exceptions import ModelAlreadyExist, WrongPassword, NoRequiredParameters


class AccountService(BaseService):
    @session_required(can_root=True)
    async def create(
            self,
            session: Session,
            username: str,
            password: str,
            role_id: int = None,
    ) -> dict:
        await self.check_username(username=username)

        password_salt = await create_salt()
        password_hash = await create_hash_by_string_and_salt(string=password, salt=password_salt)

        account = await AccountRepository().create(
            username=username,
            password_salt=password_salt,
            password_hash=password_hash,
        )

        if role_id:
            await AccountRoleService().create_by_admin(
                session=session,
                account_id=account.id,
                role_id=role_id,
            )

        await self.create_action(
            model=account,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'username': username,
            },
        )
        return {'id': account.id}

    @session_required(permissions=['accounts'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int = None,
            username: str = None,
            password: str = None,
            is_active: bool = None,
    ):
        if id_:
            account: Account = await AccountRepository().get_by_id(id_=id_)
        else:
            account: Account = session.account

        if username and account.username != username:
            await self.check_username(username=username)

        if not username and not password and not is_active:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': ['username', 'password', 'is_active']
                }
            )

        if password:
            password_salt = await create_salt()
            password_hash = await create_hash_by_string_and_salt(string=password, salt=password_salt)
        else:
            password_salt = None
            password_hash = None

        action_parameters = {
            'updater': f'session_{session.id}',
            'username': username,
            'by_admin': True,
        }

        if is_active is not None:
            action_parameters['is_active'] = is_active

        await AccountRepository().update(
            model=account,
            username=username,
            password_salt=password_salt,
            password_hash=password_hash,
            is_active=is_active,
        )

        await self.create_action(
            model=account,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required()
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        account = await AccountRepository().get_by_id(id_=id_)

        await AccountRepository().delete(model=account)

        await self.create_action(
            model=account,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
            },
        )
        return {}

    @staticmethod
    async def check_username(
            username: str,
    ):
        if await AccountRepository.is_exist_by_username(username=username):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Account',
                    'id_type': 'username',
                    'id_value': username,
                }
            )
        return {}

    @session_required(return_model=False, permissions=['accounts'])
    async def get_by_id(self, id_: int) -> dict:
        account = await AccountRepository().get_by_id(id_=id_)
        return {
            'account': await self.generate_account_dict(account)
        }

    @session_required(return_account=True)
    async def get(self, account: Account) -> dict:
        return {
            'account': await self.generate_account_dict(account, with_permissions=True)
        }

    @session_required(return_model=False)
    async def get_list(self):
        accounts = await AccountRepository().get_list()
        return {
            'accounts': [
                await self.generate_account_dict(account)
                for account in accounts
            ]
        }

    async def check_password(
            self,
            account: Account,
            password: str,
    ):
        await self._is_correct_password(account=account, password=password)

    @staticmethod
    async def _is_correct_password(account: Account, password: str):
        if account.password_hash == await create_hash_by_string_and_salt(
                string=password,
                salt=account.password_salt,
        ):
            return True
        else:
            raise WrongPassword()

    @staticmethod
    async def generate_account_dict(account: Account, with_permissions: bool = False):
        roles = await AccountRoleRepository.get_list_by_account(account=account)

        account_dict = {
            'id': account.id,
            'username': account.username,
            'roles': [
                {
                    'id': role.id,
                    'name': role.role.name,
                    'role_id': role.role.id,
                }
                for role in roles
            ],
            'is_active': account.is_active,
        }

        if with_permissions:
            permissions = await AccountRoleRepository().get_account_permissions(account=account, only_id_str=True)
            permissions = list(set(permissions))
            account_dict['permissions'] = permissions
        return account_dict
