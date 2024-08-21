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


from peewee import PrimaryKeyField, BooleanField, FloatField, CharField

from .base import BaseModel


class Promotion(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=128)
    referrer_bonus = FloatField()
    referral_bonus = FloatField()
    sms_text_partner_create = CharField(max_length=1024, null=True)
    sms_text_for_referral = CharField(max_length=1024, null=True)
    sms_text_referral_bonus = CharField(max_length=1024, null=True)
    sms_text_referrer_bonus = CharField(max_length=1024, null=True)
    is_deleted = BooleanField(default=False)

    class Meta:
        db_table = 'promotions'
