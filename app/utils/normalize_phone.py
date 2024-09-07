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


import re


def normalize_phone_number(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and (digits.startswith('8') or digits.startswith('7')):
        return '+7' + digits[1:]
    elif len(digits) == 10:
        return '+7' + digits
    else:
        raise ValueError(f'Некорректный формат номера телефона: {phone}')
