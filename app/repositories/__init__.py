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


from .account import AccountRepository
from .account_role import AccountRoleRepository
from .action import ActionRepository
from .permission import PermissionRepository
from .role import RoleRepository
from .role_permission import RolePermissionRepository
from .session import SessionRepository

from .promotion import PromotionRepository
from .partner import PartnerRepository
from .click import ClickRepository
from .referral import ReferralRepository
from .client import ClientRepository
from .lead import LeadRepository
from .sms import SmsRepository
