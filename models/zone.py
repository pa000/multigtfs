#
# Copyright 2012-2014 John Whitlock
#
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
from __future__ import unicode_literals


from multigtfs.models.base import models, Base


class Zone(Base):
    """Represents a fare zone.

    This data is not represented as a file in the GTFS.  It appears as an
    identifier in the fare_rules and the stop tables.
    """

    feed = models.ForeignKey("Feed", on_delete=models.CASCADE)
    zone_id = models.CharField(
        max_length=63, db_index=True, help_text="Unique identifier for a zone."
    )

    def __str__(self):
        return "%d-%s" % (self.feed_id, self.zone_id)

    class Meta:
        db_table = "zone"
        app_label = "multigtfs"
