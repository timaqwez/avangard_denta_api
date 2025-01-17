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

from app.services import ClientService
from app.utils import Router, Response


router = Router(
    prefix='/create',
)


class ClientCreateByAdminSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    fullname: str = Field()
    phone: str = Field(max_length=16)
    email: Optional[str] = Field(max_length=128, default=None)
    is_partner: Optional[bool] = Field()


@router.post()
async def route(schema: ClientCreateByAdminSchema):
    result = await ClientService().create_by_admin(
        token=schema.token,
        fullname=schema.fullname,
        email=schema.email,
        phone=schema.phone,
        is_partner=schema.is_partner,
    )
    return Response(**result)
