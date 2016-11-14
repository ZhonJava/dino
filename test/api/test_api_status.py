# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from test.utils import BaseTest
from activitystreams import parse as as_parser

from dino import api


class ApiStatusTest(BaseTest):
    def test_status_online(self):
        act = self.activity_for_status('online')
        response_data = api.on_status(act, as_parser(act))
        self.assertEqual(200, response_data[0])

    def test_status_invisible(self):
        act = self.activity_for_status('invisible')
        response_data = api.on_status(act, as_parser(act))
        self.assertEqual(200, response_data[0])

    def test_status_offline(self):
        act = self.activity_for_status('offline')
        response_data = api.on_status(act, as_parser(act))
        self.assertEqual(200, response_data[0])
