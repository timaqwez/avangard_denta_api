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


from peewee import DoesNotExist

from app.db.models.base import BaseModel
from app.utils.exceptions import ModelDoesNotExist


class BaseRepository:
    model: BaseModel
    model_name: str

    def __init__(self, model: BaseModel = None):
        if model:
            self.model = model

    async def is_exist(self, id_: str) -> bool:
        try:
            self.model.get((self.model.id == id_) & (self.model.is_deleted == False))
            return True
        except DoesNotExist:
            return False

    async def is_exist_by_id_str(self, id_str: str) -> bool:
        try:
            if hasattr(self.model, 'is_deleted'):
                self.model.get((self.model.id_str == id_str) & (self.model.is_deleted == False))
                return True
            else:
                self.model.get((self.model.id_str == id_str))
                return True
        except DoesNotExist:
            return False

    async def create(self, **kwargs):
        return self.model.create(**kwargs)

    async def get_list(self) -> list[BaseModel]:
        if hasattr(self.model, 'is_deleted'):
            return self.model.select().where(self.model.is_deleted == False).execute()
        else:
            return self.model.select().execute()

    async def get_by_id(self, id_: int) -> BaseModel:
        try:
            if hasattr(self.model, 'is_deleted'):
                model = self.model.get(
                    (self.model.id == id_) &
                    (self.model.is_deleted == False)
                )
            else:
                model = self.model.get(
                    (self.model.id == id_)
                )
            return model
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': self.model.__name__,
                    'id_type': 'id',
                    'id_value': id_,
                },
            )

    async def get_by_id_str(self, id_str: str) -> BaseModel:
        try:
            if hasattr(self.model, 'is_deleted'):
                model = self.model.get(
                    (self.model.id_str == id_str) &
                    (self.model.is_deleted == False)
                )
            else:
                model = self.model.get(
                    (self.model.id_str == id_str)
                )
            return model
        except DoesNotExist:
            raise ModelDoesNotExist(
                kwargs={
                    'model': self.model.__name__,
                    'id_type': 'id_str',
                    'id_value': id_str,
                },
            )

    @staticmethod
    async def update(model, **kwargs):
        for key, value in kwargs.items():
            if key[-1] == '_':
                key = key[:-1]
            if isinstance(value, int) and value == -1:
                exec(f'model.{key} = None')
            elif isinstance(value, bool) and value == False:
                exec(f'model.{key} = False')
            elif isinstance(value, bool) and value == True:
                exec(f'model.{key} = True')
            elif isinstance(value, int) and value == 0:
                exec(f'model.{key} = 0')
            elif isinstance(value, float) and value == 0:
                exec(f'model.{key} = 0')
            elif isinstance(value, str) and value == 'null':
                exec(f'model.{key} = None')
            elif value:
                exec(f'model.{key} = value')
        model.save()

    @staticmethod
    async def delete(model: BaseModel) -> BaseModel:
        if hasattr(model, 'is_deleted'):
            model.is_deleted = True
            model.save()
            return model
        else:
            model.delete_instance()
            model.save()
