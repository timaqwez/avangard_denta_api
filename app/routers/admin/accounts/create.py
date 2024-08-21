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

from pydantic import BaseModel, Field

from app.services import AccountService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class CreateAccountSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    username: str = Field(min_length=6, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    role_id: Optional[int] = Field(default=0)


@router.post()
async def route(schema: CreateAccountSchema):
    result = await AccountService().create(
        token=schema.token,
        username=schema.username,
        password=schema.password,
        role_id=schema.role_id,
    )
    return Response(**result)
