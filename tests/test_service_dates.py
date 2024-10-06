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

from datetime import date, datetime, timedelta
from hypothesis.extra.django import TestCase, from_model
from hypothesis import Verbosity, assume, example, given, note, settings
import hypothesis.strategies as st
from multigtfs.models.feed import Feed
from multigtfs.models.feed_info import FeedInfo
from multigtfs.models.service import Service
from multigtfs.models.service_date import ServiceDate
from multigtfs.models.service_dates import ServiceDates

MIN_DATE = date(2023, 1, 1)
MAX_DATE = date(2024, 6, 1)


@st.composite
def feed_infos(draw, feed: Feed, max_duration=100):
    duration = draw(st.integers(min_value=0, max_value=max_duration))
    start_date = draw(st.dates(min_value=MIN_DATE, max_value=MAX_DATE))
    end_date = start_date + timedelta(days=duration)

    return draw(
        from_model(
            FeedInfo,
            feed=st.just(feed),
            start_date=st.just(start_date),
            end_date=st.just(end_date),
        )
    )


def generate_with_feed_info(feed: Feed):
    return feed_infos(feed).map(lambda _: feed)


feeds = from_model(Feed).flatmap(generate_with_feed_info)


@st.composite
def services(draw, feed: Feed):
    start_date = draw(
        st.dates(min_value=feed.feedinfo.start_date, max_value=feed.feedinfo.end_date)
    )
    end_date = draw(st.dates(min_value=start_date, max_value=feed.feedinfo.end_date))
    return draw(
        from_model(
            Service,
            feed=st.just(feed),
            start_date=st.just(start_date),
            end_date=st.just(end_date),
            monday=st.booleans(),
            tuesday=st.booleans(),
            wednesday=st.booleans(),
            thursday=st.booleans(),
            friday=st.booleans(),
            saturday=st.booleans(),
            sunday=st.booleans(),
        )
    )


def feed_active_on(feed: Feed, d: date) -> bool:
    return (
        feed.feedinfo.start_date <= d <= feed.feedinfo.end_date
        and not FeedInfo.objects.filter(
            start_date__gt=feed.feedinfo.start_date, start_date__lte=d, end_date__gte=d
        ).exists()
    )


def base_service_active_on(service: Service, d: date) -> bool:
    assert service.start_date is not None and service.end_date is not None

    return (
        service.start_date <= d
        and d <= service.end_date
        and [
            service.monday,
            service.tuesday,
            service.wednesday,
            service.thursday,
            service.friday,
            service.saturday,
            service.sunday,
        ][d.isoweekday() - 1]
    )


@st.composite
def service_date_lists(draw, service: Service):
    dates = draw(
        st.sets(
            st.dates(
                min_value=service.feed.feedinfo.start_date,
                max_value=service.feed.feedinfo.end_date,
            ),
            max_size=10,
        )
    )

    service_dates = [
        draw(
            from_model(
                ServiceDate,
                service=st.just(service),
                date=st.just(d),
                exception_type=st.just(2)
                if base_service_active_on(service, d)
                else st.just(1),
            )
        )
        for d in dates
    ]
    return service_dates


def generate_with_service_dates(service: Service):
    return service_date_lists(service).map(lambda _: service)


def count_days_active(service: Service) -> int:
    assert service.start_date is not None
    assert service.end_date is not None

    service_dates = {}

    for sd in ServiceDate.objects.filter(service=service):
        assert sd.date not in service_dates
        service_dates[sd.date] = sd.exception_type

    count = sum(et == 1 for et in service_dates.values())

    for d in [
        service.start_date + timedelta(days=dt)
        for dt in range((service.end_date - service.start_date).days + 1)
    ]:
        if d in service_dates:
            continue

        count += base_service_active_on(service, d) and feed_active_on(service.feed, d)

    return count


class TestServiceDates(TestCase):
    @settings(deadline=timedelta(seconds=1))
    @given(service=feeds.flatmap(services))
    def test_one_service(self, service: Service):
        ServiceDates.refresh()
        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(ServiceDates.objects.count(), count_days_active(service))

    @settings(deadline=timedelta(seconds=1))
    @given(services=feeds.flatmap(lambda f: st.lists(services(f), max_size=100)))
    def test_many_services(self, services: list[Service]):
        ServiceDates.refresh()
        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(
            ServiceDates.objects.count(), sum(map(count_days_active, services))
        )

    @settings(deadline=timedelta(seconds=1))
    @given(service=feeds.flatmap(services).flatmap(generate_with_service_dates))
    def test_one_service_many_dates(self, service):
        ServiceDates.refresh()
        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(ServiceDates.objects.count(), count_days_active(service))

    @settings(deadline=timedelta(seconds=1))
    @given(
        services=feeds.flatmap(
            lambda f: st.lists(
                services(f).flatmap(generate_with_service_dates), max_size=30
            )
        )
    )
    def test_many_services_many_dates(self, services):
        ServiceDates.refresh()
        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(
            ServiceDates.objects.count(), sum(map(count_days_active, services))
        )

    @settings(deadline=timedelta(seconds=1))
    @given(
        services=st.lists(
            feeds.flatmap(lambda f: st.lists(services(f), max_size=5)),
            max_size=3,
        ).flatmap(lambda l: st.just([x for xs in l for x in xs]))
    )
    def test_many_feeds(self, services):
        ServiceDates.refresh()

        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(
            ServiceDates.objects.count(),
            sum(map(count_days_active, services)),
            "Wrong service dates count",
        )

    @settings(deadline=timedelta(seconds=1))
    @given(
        services=st.lists(
            feeds.flatmap(
                lambda f: st.lists(
                    services(f).flatmap(generate_with_service_dates), max_size=5
                )
            ),
            max_size=3,
        ).flatmap(lambda l: st.just([x for xs in l for x in xs]))
    )
    def test_many_feeds_many_dates(self, services):
        ServiceDates.refresh()

        note(str(Service.objects.all().values()))
        note(str(ServiceDates.objects.all().values()))
        note(str(FeedInfo.objects.values()))

        self.assertEqual(
            ServiceDates.objects.count(),
            sum(map(count_days_active, services)),
            "Wrong service dates count",
        )
