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


import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks.permanents.sync_gd import sync_gd

prefix = '[start_app]'


TASKS = [
    sync_gd,
]


async def start_app() -> None:
    scheduler = AsyncIOScheduler()
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    while True:
        tasks_names = [task.get_name() for task in asyncio.all_tasks()]
        [asyncio.create_task(coro=task(scheduler), name=task.__name__) for task in TASKS if task.__name__ not in tasks_names]
        await asyncio.sleep(10 * 60)
