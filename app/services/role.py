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


from app.db.models import Role, Session
from app.repositories import RolePermissionRepository, RoleRepository
from app.services.base import BaseService
from app.utils.decorators import session_required


class RoleService(BaseService):
    @session_required(permissions=['roles'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
    ):
        role = await RoleRepository().create(
            name=name,
        )

        await self.create_action(
            model=role,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'by_admin': True,
            }
        )

        return {'id': role.id}

    @session_required(permissions=['roles'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        role = await RoleRepository().get_by_id(id_=id_)

        await RoleRepository().delete(model=role)

        await self.create_action(
            model=role,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['roles'], return_model=False, can_root=True)
    async def get(
            self,
            id_: int,
    ):
        role: Role = await RoleRepository().get_by_id(id_=id_)
        return {
            'role': {
                'id': role.id,
                'name': role.name,
                'permissions': await RolePermissionRepository().get_permissions_by_role(role=role, only_id_str=True)
            }
        }

    @session_required(permissions=['roles'], return_model=False, can_root=True)
    async def get_list(self):
        return {
            'roles': [
                {
                    'id': role.id,
                    'name': role.name,
                    'permissions': await RolePermissionRepository().get_permissions_by_role(role=role, only_id_str=True)
                } for role in await RoleRepository().get_list()
            ]
        }
