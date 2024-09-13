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
import logging

from addict import Dict
from aiohttp import ClientSession
from gspread import Spreadsheet

from app.utils.normalize_phone import normalize_phone_number
from config import settings
from ..utils.google_sheets_api_client import google_sheets_api_client


async def sync_partners(table: Spreadsheet):

    def find_expired_partners(promotion_partners, sheet_partners):
        promotion_partners_phones = {partner['phone'] for partner in promotion_partners if 'phone' in partner}
        sheet_partners_phones = {partner['Телефон'] for partner in sheet_partners if 'Телефон' in partner}
        expired = promotion_partners_phones - sheet_partners_phones
        new = sheet_partners_phones - expired - promotion_partners_phones
        return expired, new

    async with ClientSession(settings.api_url) as session:
        async with session.get(
            url='/admin/promotions/list/get',
            params={
                'token': f'0:{settings.root_token}',
            },
        ) as r:
            promotions = (await r.json())['promotions']

        for promotion in promotions:
            promotion = Dict(**promotion)
            try:
                sheet = await google_sheets_api_client.get_sheet_by_table_and_name(table=table, name=promotion.name)
            except Exception:
                continue
            rows = await google_sheets_api_client.get_rows(sheet=sheet)
            for row in rows:
                row.Телефон = normalize_phone_number(row.Телефон)
            expired_partners_phones, new_partners_phones = find_expired_partners(
                promotion_partners=promotion.partners,
                sheet_partners=rows,
            )
            for phone in expired_partners_phones:
                await session.post(
                    url='/admin/partners/delete/by-phone',
                    json={
                        'token': f'0:{settings.root_token}',
                        'phone': phone,
                        'promotion_id': promotion.id,
                    },
                )
            for row in rows:
                if row.Телефон in new_partners_phones:
                    async with session.post(
                        url='/admin/clients/create',
                        json={
                            'token': f'0:{settings.root_token}',
                            'fullname': row.Имя,
                            'phone': row.Телефон,
                            'is_partner': True,
                        },
                    ) as r:
                        data = Dict(**await r.json())
                        if data.state == 'error':
                            client_id = data.error.kwargs.model_id
                        else:
                            client_id = data.id
                        logging.log(level=1, msg='Partner create...')
                        response = await session.post(
                            url='/admin/partners/create',
                            json={
                                'token': f'0:{settings.root_token}',
                                'promotion_id': promotion.id,
                                'client_id': client_id,
                            },
                        )
                        logging.log(level=logging.INFO, msg=await response.json())


