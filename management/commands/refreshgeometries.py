#
# Copyright 2012-2014 John Whitlock
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
from __future__ import unicode_literals
import logging
import time

from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from geohelper import fix_unmonotone_stops
from multigtfs.models import Feed, Route, Shape, Trip, StopTime
from multigtfs.models.service_dates import ServiceDates
from multigtfs.models.stop import Stop
from multigtfs.models.trip_time import TripTime


class Command(BaseCommand):
    help = "Updates the cached geometry of GTFS feeds"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("feed_ids", nargs="*", metavar="Feed ID", type=int)

        # Named (optional) arguments
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            dest="all",
            default=False,
            help="Update all feeds",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_false",
            dest="verbose",
            default=True,
            help="Don't print status messages to stdout",
        )

    def handle(self, *args, **options):
        total_start = time.time()

        # Validate the arguments
        all_feeds = options.get("all")
        feed_ids = options.get("feed_ids")
        if len(feed_ids) == 0 and not all_feeds:
            raise CommandError("You must pass in a feed ID or --all.")
        if len(feed_ids) > 0 and all_feeds:
            raise CommandError("You can't specify a feed and --all.")

        # Setup logging
        verbosity = int(options["verbosity"])
        console = logging.StreamHandler(self.stderr)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        logger_name = "multigtfs"
        if verbosity == 0:
            level = logging.WARNING
        elif verbosity == 1:
            level = logging.INFO
        elif verbosity == 2:
            level = logging.DEBUG
        else:
            level = logging.DEBUG
            logger_name = ""
            formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        console.setLevel(level)
        console.setFormatter(formatter)
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.addHandler(console)

        # Disable database query logging
        if settings.DEBUG:
            connection.use_debug_cursor = False

        # Get the feeds
        if all_feeds:
            feeds = Feed.objects.order_by("id")
        else:
            feeds = []
            for feed_id in feed_ids:
                try:
                    feeds.append(Feed.objects.get(id=feed_id))
                except Feed.DoesNotExist:
                    raise CommandError("Feed %s not found" % feed_id)

        # Refresh the geometries
        for feed in feeds:
            logger.info("Updating geometries in Feed %s (ID %s)...", feed.name, feed.id)

            start_time = time.time()
            stops = Stop.objects.in_feed(feed)
            end_time = time.time()
            logger.debug(
                "Imported %s stop%s in %0.1f seconds",
                stops.count(),
                "" if stops.count() == 1 else "s",
                end_time - start_time,
            )

            start_time = time.time()
            shapes = Shape.objects.in_feed(feed)
            for shape in shapes:
                shape.update_geometry(update_parent=False)
            end_time = time.time()
            logger.debug(
                "Imported %s shape%s in %0.1f seconds",
                shapes.count(),
                "" if shapes.count() == 1 else "s",
                end_time - start_time,
            )

            start_time = time.time()
            trips = Trip.objects.in_feed(feed)
            for trip in trips:
                trip.update_geometry(update_parent=False)
            end_time = time.time()
            logger.debug(
                "Imported %s trip%s in %0.1f seconds",
                trips.count(),
                "" if trips.count() == 1 else "s",
                end_time - start_time,
            )

            start_time = time.time()
            routes = Route.objects.in_feed(feed)
            for route in routes:
                route.update_geometry()
            end_time = time.time()
            logger.debug(
                "Imported %s route%s in %0.1f seconds",
                routes.count(),
                "" if routes.count() == 1 else "s",
                end_time - start_time,
            )

            start_time = time.time()
            StopTime.objects.update()
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE stop_time SET shape_dist_traveled = ST_LineLocatePoint(ST_Transform(t.geometry, 32633), ST_Transform(s.point, 32633)) * ST_Length(ST_Transform(t.geometry, 32633)) FROM trip t, stop s WHERE t.id = stop_time.trip_id AND s.id = stop_time.stop_id AND s.feed_id = %s",
                    [feed.id],
                )
                stop_time_count = cursor.rowcount
            end_time = time.time()
            logger.debug(
                "Imported geometries for %d stop_times in %0.1f seconds",
                stop_time_count,
                end_time - start_time,
            )

            ServiceDates.refresh()
            logger.info("Refreshed service dates materialized view")

            TripTime.refresh()
            logger.info("Refreshed trip time materialized view")

            fix_unmonotone_stops()

            total_end = time.time()
            logger.info(
                "Feed %d: Updated geometries in %d shape%s, %d trip%s, and"
                " %d route%s %0.1f seconds.",
                feed.id,
                shapes.count(),
                "" if shapes.count() == 1 else "s",
                trips.count(),
                "" if trips.count() == 1 else "s",
                routes.count(),
                "" if routes.count() == 1 else "s",
                total_end - total_start,
            )
