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


from pydantic import BaseModel, Field

from app.services import PartnerService
from app.utils import Router
from app.utils.response import Response


router = Router(
    prefix='/codes/check',
)


class PartnerCodeCheckSchema(BaseModel):
    code: str = Field()


@router.post()
async def route(schema: PartnerCodeCheckSchema):
    result = await PartnerService().check_code(
        base64code=schema.code,
    )
    return Response(**result)
