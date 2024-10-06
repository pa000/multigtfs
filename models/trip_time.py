#
# Copyright 2024 Filip Pazera
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

from django.db import connection, models
from multigtfs.models.fields.seconds import SecondsField

from multigtfs.models.trip import Trip


class TripTime(models.Model):
    trip = models.OneToOneField(
        Trip, primary_key=True, on_delete=models.DO_NOTHING, db_index=True
    )
    start_time = SecondsField()
    end_time = SecondsField()

    def __str__(self):
        return "%s %s-%s" % (self.trip, self.start_time, self.end_time)

    @classmethod
    def refresh(cls):
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY trip_time")

    class Meta:
        managed = False
        db_table = "trip_time"
