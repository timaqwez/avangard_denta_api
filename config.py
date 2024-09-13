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


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_port: int
    api_url: str

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_name: str

    sms_request_url: str
    sms_request_login: str
    sms_request_password: str
    sms_request_sender: str

    referral_site_url: str

    root_token: str
    tasks_token: str

    sync_partners_table_name: str

    items_per_page: int = 10

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
