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


from fastapi.responses import RedirectResponse

from .clicks import router as router_clicks
from .sessions import router as router_sessions
from .tasks import router as router_tasks
from .partners import router as router_partners
from .leads import router as router_leads
from app.utils import Router

router = Router(
    prefix='',
    routes_included=[
        router_sessions,
        router_clicks,
        router_tasks,
        router_leads,
        router_partners,
    ],
)


@router.get('/', include_in_schema=False)
async def route():
    return RedirectResponse('/docs')

