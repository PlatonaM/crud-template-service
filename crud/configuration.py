"""
   Copyright 2020 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("crud_conf",)


import simple_env_var


@simple_env_var.configuration
class CRUDConf:

    @simple_env_var.section
    class Logger:
        name = "crud-template"
        level = "info"

    @simple_env_var.section
    class Endpoint:
        name = None
        content_type = "application/json"
        allow_post = False
        full_collection = False


crud_conf = CRUDConf(load=False)
