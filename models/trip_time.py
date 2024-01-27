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
