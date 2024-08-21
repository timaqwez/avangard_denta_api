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
from datetime import datetime, timedelta
from typing import Optional

from app.services.lead import LeadService
from app.services.partner import PartnerService
from app.services.base import BaseService
from app.repositories import PromotionRepository, ReferralRepository, PartnerRepository, ClickRepository
from app.db.models import Promotion, Session, Partner
from app.utils.decorators import session_required
from app.utils.exceptions import NoRequiredParameters


class PromotionService(BaseService):
    @session_required(permissions=['promotions'], can_root=True)
    async def create_by_admin(
            self,
            session: Session,
            name: str,
            referrer_bonus: float,
            referral_bonus: float,
            sms_text_partner_create: str = None,
            sms_text_for_referral: str = None,
            sms_text_referral_bonus: str = None,
            sms_text_referrer_bonus: str = None,
    ):
        promotion = await PromotionRepository().create(
            name=name,
            referrer_bonus=referrer_bonus,
            referral_bonus=referral_bonus,
            sms_text_partner_create=sms_text_partner_create,
            sms_text_for_referral=sms_text_for_referral,
            sms_text_referral_bonus=sms_text_referral_bonus,
            sms_text_referrer_bonus=sms_text_referrer_bonus,
        )

        await self.create_action(
            model=promotion,
            action='create',
            parameters={
                'creator': f'session_{session.id}',
                'name': name,
                'referrer_bonus': referrer_bonus,
                'referral_bonus': referral_bonus,
                'sms_text_partner_create': sms_text_partner_create,
                'sms_text_for_referral': sms_text_for_referral,
                'sms_text_referral_bonus': sms_text_referral_bonus,
                'sms_text_referrer_bonus': sms_text_referrer_bonus,
                'by_admin': True,
            }
        )

        return {'id': promotion.id}

    @session_required(permissions=['promotions'])
    async def update_by_admin(
            self,
            session: Session,
            id_: int,
            referral_bonus: Optional[float],
            referrer_bonus: Optional[float],
            sms_text_partner_create: str = None,
            sms_text_for_referral: str = None,
            sms_text_referral_bonus: str = None,
            sms_text_referrer_bonus: str = None,
    ):
        promotion: Promotion = await PromotionRepository().get_by_id(id_=id_)

        if not referral_bonus \
                and not referrer_bonus \
                and not sms_text_partner_create \
                and not sms_text_for_referral \
                and not sms_text_referral_bonus \
                and not sms_text_referrer_bonus:
            raise NoRequiredParameters(
                kwargs={
                    'parameters': [
                        'referral_bonus',
                        'referrer_bonus',
                        'sms_text_partner_create',
                        'sms_text_for_referral',
                        'sms_text_referral_bonus',
                        'sms_text_referrer_bonus',
                    ]
                }
            )
        ''
        action_parameters = {
            'updater': f'session_{session.id}',
            'by_admin': True,
        }

        if referral_bonus is not None:
            action_parameters['referral_bonus'] = referral_bonus

        if referrer_bonus is not None:
            action_parameters['referrer_bonus'] = referrer_bonus

        if sms_text_partner_create:
            action_parameters['sms_text_partner_create'] = sms_text_partner_create

        if sms_text_for_referral:
            action_parameters['sms_text_for_referral'] = sms_text_for_referral

        if sms_text_referral_bonus:
            action_parameters['sms_text_referral_bonus'] = sms_text_referral_bonus

        if sms_text_referrer_bonus:
            action_parameters['sms_text_referrer_bonus'] = sms_text_referrer_bonus

        await PromotionRepository().update(
            model=promotion,
            referral_bonus=referral_bonus,
            referrer_bonus=referrer_bonus,
            sms_text_for_referral=sms_text_for_referral,
            sms_text_partner_create=sms_text_partner_create,
            sms_text_referral_bonus=sms_text_referral_bonus,
            sms_text_referrer_bonus=sms_text_referrer_bonus,
        )

        await self.create_action(
            model=promotion,
            action='update',
            parameters=action_parameters,
        )

        return {}

    @session_required(permissions=['promotions'], can_root=True)
    async def delete_by_admin(
            self,
            session: Session,
            id_: int,
    ):
        promotion = await PromotionRepository().get_by_id(id_=id_)

        await PromotionRepository().delete(model=promotion)

        await self.create_action(
            model=promotion,
            action='delete',
            parameters={
                'deleter': f'session_{session.id}',
                'by_admin': True,
            }
        )

        return {}

    @session_required(permissions=['promotions'], return_model=False)
    async def get_by_admin(
            self,
            id_: int,
    ):
        promotion: Promotion = await PromotionRepository().get_by_id(id_=id_)
        partners: list[Partner] = await PartnerRepository().get_list_by_promotion(promotion)
        return {
            'promotion': await self.generate_promotion_dict(promotion, partners)
        }

    @session_required(permissions=['promotions'], return_model=False, can_root=True)
    async def get_list_by_admin(self):
        return {
            'promotions': [
                await self.generate_promotion_dict(promotion,
                                                   partners=await PartnerRepository().get_list_by_promotion(promotion))
                for promotion in await PromotionRepository().get_list()
            ]
        }

    async def generate_promotion_dict(self, promotion: Promotion, partners: list[Partner]):
        partners = await PartnerRepository().get_list_by_promotion(promotion=promotion)
        leads = []
        for partner in partners:
            for lead in partner.leads:
                leads.append(lead)
        total_referrals, week_referrals, day_referrals = await self.get_referrals_count(partners=partners)
        total_clicks, week_clicks, day_clicks = await self.get_clicks_count(partners=partners)
        total_leads, week_leads, day_leads = await self.get_leads_count(partners=partners)
        return {
            'id': promotion.id,
            'name': promotion.name,
            'referrer_bonus': promotion.referrer_bonus,
            'referral_bonus': promotion.referral_bonus,
            'total_referrals': total_referrals,
            'week_referrals': week_referrals,
            'day_referrals': day_referrals,
            'total_clicks': total_clicks,
            'week_clicks': week_clicks,
            'day_clicks': day_clicks,
            'total_leads': total_leads,
            'week_leads': week_leads,
            'day_leads': day_leads,
            'sms_text_partner_create': promotion.sms_text_partner_create,
            'sms_text_for_referral': promotion.sms_text_for_referral,
            'sms_text_referral_bonus': promotion.sms_text_referral_bonus,
            'sms_text_referrer_bonus': promotion.sms_text_referrer_bonus,
            'partners': [
                await PartnerService().generate_partner_dict(partner)
                for partner in partners
            ],
            'leads': [
                await LeadService().generate_lead_dict(lead)
                for lead in leads
            ]
        }

    @staticmethod
    async def get_referrals_count(partners: list[Partner]):
        total_referrals, week_referrals, day_referrals = 0, 0, 0
        for partner in partners:
            referrals = await ReferralRepository().get_list_by_partner(partner=partner)
            for referral in referrals:
                total_referrals += 1
                if referral.created_at > datetime.now() - timedelta(days=7):
                    week_referrals += 1
                    if referral.created_at > datetime.now() - timedelta(days=1):
                        day_referrals += 1
        return total_referrals, week_referrals, day_referrals

    @staticmethod
    async def get_clicks_count(partners: list[Partner]):
        total_clicks, week_clicks, day_clicks = 0, 0, 0
        for partner in partners:
            clicks = partner.clicks
            for click in clicks:
                total_clicks += 1
                if click.created_at > datetime.now() - timedelta(days=7):
                    week_clicks += 1
                    if click.created_at > datetime.now() - timedelta(days=1):
                        day_clicks += 1
        return total_clicks, week_clicks, day_clicks

    @staticmethod
    async def get_leads_count(partners: list[Partner]):
        total_leads, week_leads, day_leads = 0, 0, 0
        for partner in partners:
            leads = partner.leads
            for lead in leads:
                total_leads += 1
                if lead.created_at > datetime.now() - timedelta(days=7):
                    week_leads += 1
                    if lead.created_at > datetime.now() - timedelta(days=1):
                        day_leads += 1
        return total_leads, week_leads, day_leads
