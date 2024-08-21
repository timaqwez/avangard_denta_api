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


from .accounts import router as router_accounts
from .permissions import router as router_permissions
from .roles import router as router_roles
from .leads import router as router_leads
from .promotions import router as router_promotions
from .clicks import router as router_clicks
from .referrals import router as router_referrals
from .partners import router as router_partners
from .clients import router as router_clients
from app.utils import Router


router = Router(
    prefix='/admin',
    routes_included=[
        router_accounts,
        router_roles,
        router_leads,
        router_permissions,
        router_promotions,
        router_partners,
        router_referrals,
        router_clicks,
        router_clients,
    ],
)
