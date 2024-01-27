from datetime import timedelta
from django.db import connection, models

from .feed_info import FeedInfo
from multigtfs.models.service import Service


class ServiceDates(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(db_index=True)

    def __str__(self):
        return "%s %s" % (self.service, self.date)

    @classmethod
    def refresh(cls):
        ServiceDates.objects.all().delete()
        for service in Service.objects.all():
            cur_date = service.start_date or service.feed.feedinfo.start_date
            end_date = service.end_date or service.feed.feedinfo.end_date

            dates = set(
                service.servicedate_set.filter(exception_type=1).values_list(
                    "date", flat=True
                )
            )

            while cur_date <= end_date:
                if (
                    other_fi := FeedInfo.objects.filter(
                        start_date__gt=service.feed.feedinfo.start_date,
                        start_date__lte=cur_date,
                        end_date__gte=cur_date,
                    )
                    .order_by("start_date")
                    .first()
                ) is not None:
                    if other_fi.end_date is not None:
                        cur_date = other_fi.end_date + timedelta(days=1)
                        continue

                if service.servicedate_set.filter(
                    date=cur_date, exception_type=2
                ).exists():
                    cur_date += timedelta(days=1)
                    continue

                if [
                    service.monday,
                    service.tuesday,
                    service.wednesday,
                    service.thursday,
                    service.friday,
                    service.saturday,
                    service.sunday,
                ][cur_date.isoweekday() - 1]:
                    dates.add(cur_date)

                cur_date += timedelta(days=1)

            ServiceDates.objects.bulk_create(
                [ServiceDates(service=service, date=date) for date in dates]
            )

    class Meta:
        db_table = "service_dates"
