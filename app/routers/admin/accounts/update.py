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

from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

from app.services import AccountService
from app.utils import Router, Response


router = Router(
    prefix='/update',
)


class UpdateAccountSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: PositiveInt = Field()
    username: Optional[str] = Field(min_length=6, max_length=32, default=None)
    password: Optional[str] = Field(min_length=6, max_length=128, default=None)
    is_active: Optional[bool] = Field()


@router.post()
async def route(schema: UpdateAccountSchema):
    result = await AccountService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        username=schema.username,
        password=schema.password,
        is_active=schema.is_active,
    )
    return Response(**result)
