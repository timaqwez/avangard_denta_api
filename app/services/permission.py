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
from app.repositories import PermissionRepository
from app.db.models import Permission, Session
from app.utils.exceptions import ModelAlreadyExist
from app.utils.decorators import session_required


class PermissionService(BaseService):
    @session_required(permissions=['permissions'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            id_str: str,
            name: str,
    ):
        if await PermissionRepository().is_exist_by_id_str(id_str=id_str):
            raise ModelAlreadyExist(
                kwargs={
                    'model': 'Permission',
                    'id_type': 'id_str',
                    'id_value': id_str,
                }
            )

        permission = await PermissionRepository().create(
            id_str=id_str,
            name=name,
        )

        await self.create_action(
            model=permission,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'id_str': id_str,
                'name': name,
                'by_admin': True,
            }
        )

        return {'id': permission.id}

    @session_required(permissions=['permissions'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_str: str,
    ):
        permission = await PermissionRepository().get_by_id_str(id_str=id_str)

        await PermissionRepository().delete(model=permission)

        await self.create_action(
            model=permission,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'id_str': id_str,
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['permissions'], return_model=False)
    async def get_by_admin(
            self,
            id_str: str,
    ):
        permission: Permission = await PermissionRepository().get_by_id_str(id_str=id_str)
        return {
            'permission': {
                'id': permission.id,
                'id_str': permission.id_str,
                'name': permission.name,
            }
        }

    @session_required(permissions=['permissions'], return_model=False, can_root=True)
    async def get_list_by_admin(self):
        return {
            'permissions': [
                {
                    'id': permission.id,
                    'id_str': permission.id_str,
                    'name': permission.name,
                } for permission in await PermissionRepository().get_list()
            ]
        }
