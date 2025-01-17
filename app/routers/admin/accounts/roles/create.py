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


from pydantic import BaseModel, Field, PositiveInt

from app.services import AccountRoleService
from app.utils import Response, Router


router = Router(
    prefix='/create',
)


class AccountRoleCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    account_id: PositiveInt = Field()
    role_id: PositiveInt = Field()


@router.post()
async def route(schema: AccountRoleCreateByAdminSchema):
    result = await AccountRoleService().create_by_admin(
        token=schema.token,
        account_id=schema.account_id,
        role_id=schema.role_id,
    )
    return Response(**result)
