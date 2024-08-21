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

from pydantic import BaseModel, Field, PositiveInt, NonNegativeFloat

from app.services import PromotionService
from app.utils import Router, Response


router = Router(
    prefix='/update',
)


class UpdatePromotionSchema(BaseModel):
    token: str = Field(min_length=32, max_length=64)
    id: PositiveInt = Field()
    referral_bonus: Optional[NonNegativeFloat] = Field(default=None)
    referrer_bonus: Optional[NonNegativeFloat] = Field(default=None)
    sms_text_partner_create: Optional[str] = Field(max_length=1024, default=None)
    sms_text_for_referral: Optional[str] = Field(max_length=1024, default=None)
    sms_text_referral_bonus: Optional[str] = Field(max_length=1024, default=None)
    sms_text_referrer_bonus: Optional[str] = Field(max_length=1024, default=None)


@router.post()
async def route(schema: UpdatePromotionSchema):
    result = await PromotionService().update_by_admin(
        token=schema.token,
        id_=schema.id,
        referral_bonus=schema.referral_bonus,
        referrer_bonus=schema.referrer_bonus,
        sms_text_for_referral=schema.sms_text_for_referral,
        sms_text_partner_create=schema.sms_text_partner_create,
        sms_text_referral_bonus=schema.sms_text_referral_bonus,
        sms_text_referrer_bonus=schema.sms_text_referrer_bonus,
    )
    return Response(**result)
