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


from .account import Account
from .account_role import AccountRole
from .action import Action
from .action_parameter import ActionParameter
from .click import Click
from .client import Client
from .lead import Lead
from .referral import Referral
from .permission import Permission
from .promotion import Promotion
from .partner import Partner
from .role import Role
from .role_permission import RolePermission
from .session import Session
from .sms import Sms

models = (
    Account,
    Role,
    Permission,
    Session,

    Action,
    ActionParameter,

    RolePermission,
    AccountRole,

    Promotion,
    Partner,
    Client,
    Referral,
    Click,
    Lead,
    Sms,
)
