# Generated by Django 5.0.1 on 2024-01-27 17:10

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import multigtfs.models.fields.seconds
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_id', models.CharField(db_index=True, help_text='Unique identifier for a trip.', max_length=255)),
                ('headsign', models.CharField(blank=True, help_text='Destination identification for passengers.', max_length=255)),
                ('short_name', models.CharField(blank=True, help_text='Short name used in schedules and signboards.', max_length=63)),
                ('direction', models.CharField(blank=True, choices=[('0', '0'), ('1', '1')], help_text='Direction for bi-directional routes.', max_length=1)),
                ('brigade_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('geometry', django.contrib.gis.db.models.fields.LineStringField(blank=True, help_text='Geometry cache of Shape or Stops', null=True, srid=4326)),
                ('wheelchair_accessible', models.CharField(blank=True, choices=[('0', 'No information'), ('1', 'Some wheelchair accommodation'), ('2', 'No wheelchair accommodation')], help_text='Are there accommodations for riders with wheelchair?', max_length=1)),
                ('bikes_allowed', models.CharField(blank=True, choices=[('0', 'No information'), ('1', 'Some bicycle accommodation'), ('2', 'No bicycles allowed')], help_text='Are bicycles allowed?', max_length=1)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'db_table': 'trip',
            },
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_id', models.CharField(db_index=True, help_text='Unique identifier for a block.', max_length=63)),
            ],
            options={
                'db_table': 'block',
            },
        ),
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('meta', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'db_table': 'feed',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.CharField(db_index=True, help_text='Unique identifier for route.', max_length=255)),
                ('short_name', models.CharField(help_text='Short name of the route', max_length=63)),
                ('long_name', models.CharField(help_text='Long name of the route', max_length=255)),
                ('desc', models.TextField(blank=True, help_text='Long description of a route', verbose_name='description')),
                ('rtype', models.IntegerField(choices=[(0, 'Tram, Streetcar, or Light rail'), (1, 'Subway or Metro'), (2, 'Rail'), (3, 'Bus'), (4, 'Ferry'), (5, 'Cable car'), (6, 'Gondola or Suspended cable car'), (7, 'Funicular')], help_text='Type of transportation used on route', verbose_name='route type')),
                ('url', models.URLField(blank=True, help_text='Web page about for the route')),
                ('color', models.CharField(blank=True, help_text='Color of route in hex', max_length=6)),
                ('text_color', models.CharField(blank=True, help_text='Color of route text in hex', max_length=6)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(blank=True, help_text='Geometry cache of Trips', null=True, srid=4326)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
            ],
            options={
                'db_table': 'route',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(db_index=True, help_text='Unique identifier for service dates.', max_length=255)),
                ('monday', models.BooleanField(default=True, help_text='Is the route active on Monday?')),
                ('tuesday', models.BooleanField(default=True, help_text='Is the route active on Tuesday?')),
                ('wednesday', models.BooleanField(default=True, help_text='Is the route active on Wednesday?')),
                ('thursday', models.BooleanField(default=True, help_text='Is the route active on Thursday?')),
                ('friday', models.BooleanField(default=True, help_text='Is the route active on Friday?')),
                ('saturday', models.BooleanField(default=True, help_text='Is the route active on Saturday?')),
                ('sunday', models.BooleanField(default=True, help_text='Is the route active on Sunday?')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='Shape',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shape_id', models.CharField(db_index=True, help_text='Unique identifier for a shape.', max_length=255)),
                ('geometry', django.contrib.gis.db.models.fields.LineStringField(blank=True, help_text='Geometry cache of ShapePoints', null=True, srid=4326)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'db_table': 'shape',
            },
        ),
        migrations.CreateModel(
            name='TripTime',
            fields=[
                ('trip', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to='multigtfs.trip')),
                ('start_time', multigtfs.models.fields.seconds.SecondsField()),
                ('end_time', multigtfs.models.fields.seconds.SecondsField()),
            ],
            options={
                'db_table': 'trip_time',
                'managed': False,
            },
        ),
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW trip_time AS
            SELECT trip_id,
                   MIN(arrival_time) as start_time,
                   MAX(arrival_time) as end_time
            FROM stop_time
            GROUP BY trip_id
            """,
            "DROP MATERIALIZED VIEW trip_time",
        ),
        migrations.RunSQL(
            "CREATE UNIQUE INDEX trip_time_trip ON trip_time (trip_id)",
            "DROP INDEX trip_time_trip",
        ),
        migrations.AddField(
            model_name='trip',
            name='block',
            field=models.ForeignKey(blank=True, help_text='Block of sequential trips that this trip belongs to.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.block'),
        ),
        migrations.CreateModel(
            name='Fare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fare_id', models.CharField(db_index=True, help_text='Unique identifier for a fare class', max_length=255)),
                ('price', models.DecimalField(decimal_places=4, help_text='Fare price, in units specified by currency_type', max_digits=17)),
                ('currency_type', models.CharField(help_text='ISO 4217 alphabetical currency code', max_length=3)),
                ('payment_method', models.IntegerField(choices=[(0, 'Fare is paid on board.'), (1, 'Fare must be paid before boarding.')], default=1, help_text='When is the fare paid?')),
                ('transfers', models.IntegerField(blank=True, choices=[(0, 'No transfers permitted on this fare.'), (1, 'Passenger may transfer once.'), (2, 'Passenger may transfer twice.'), (None, 'Unlimited transfers are permitted.')], default=None, help_text='Are transfers permitted?', null=True)),
                ('transfer_duration', models.IntegerField(blank=True, help_text='Time in seconds until a ticket or transfer expires', null=True)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'db_table': 'fare',
            },
        ),
        migrations.AddField(
            model_name='block',
            name='feed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed'),
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency_id', models.CharField(blank=True, db_index=True, help_text='Unique identifier for transit agency', max_length=255)),
                ('name', models.CharField(help_text='Full name of the transit agency', max_length=255)),
                ('url', models.URLField(blank=True, help_text='URL of the transit agency')),
                ('timezone', models.CharField(help_text='Timezone of the agency', max_length=255)),
                ('lang', models.CharField(blank=True, help_text='ISO 639-1 code for the primary language', max_length=2)),
                ('phone', models.CharField(blank=True, help_text='Voice telephone number', max_length=255)),
                ('fare_url', models.URLField(blank=True, help_text='URL for purchasing tickets online')),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'verbose_name_plural': 'agencies',
                'db_table': 'agency',
            },
        ),
        migrations.CreateModel(
            name='FeedInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('publisher_name', models.CharField(help_text='Full name of organization that publishes the feed.', max_length=255)),
                ('publisher_url', models.URLField(help_text="URL of the feed publisher's organization.")),
                ('lang', models.CharField(help_text='IETF BCP 47 language code for text in field.', max_length=20, verbose_name='language')),
                ('start_date', models.DateField(blank=True, help_text='Date that feed starts providing reliable data.', null=True)),
                ('end_date', models.DateField(blank=True, help_text='Date that feed stops providing reliable data.', null=True)),
                ('version', models.CharField(blank=True, help_text='Version of feed.', max_length=255)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('feed', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'verbose_name_plural': 'feed info',
                'db_table': 'feed_info',
            },
        ),
        migrations.CreateModel(
            name='Frequency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', multigtfs.models.fields.seconds.SecondsField(help_text='Time that the service begins at the specified frequency')),
                ('end_time', multigtfs.models.fields.seconds.SecondsField(help_text='Time that the service ends at the specified frequency')),
                ('headway_secs', models.IntegerField(help_text='Time in seconds before returning to same stop')),
                ('exact_times', models.CharField(blank=True, choices=[('0', 'Trips are not exactly scheduled'), ('1', 'Trips are exactly scheduled from start time')], help_text='Should frequency-based trips be exactly scheduled?', max_length=1)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.trip')),
            ],
            options={
                'verbose_name_plural': 'frequencies',
                'db_table': 'frequency',
            },
        ),
        migrations.AddField(
            model_name='trip',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.route'),
        ),
        migrations.AddField(
            model_name='route',
            name='agency',
            field=models.ForeignKey(blank=True, help_text='Agency for this route.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.agency'),
        ),
        migrations.AddField(
            model_name='route',
            name='feed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed'),
        ),
        migrations.AddField(
            model_name='trip',
            name='service',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.service'),
        ),
        migrations.CreateModel(
            name='ServiceDate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(help_text='Date that the service differs from the norm.')),
                ('exception_type', models.IntegerField(choices=[(1, 'Added'), (2, 'Removed')], default=1, help_text='Is service added or removed on this date?')),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.service')),
            ],
            options={
                'db_table': 'service_date',
            },
        ),
        migrations.CreateModel(
            name='ServiceDates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.service')),
            ],
            options={
                'db_table': 'service_dates',
            },
        ),
        migrations.AddField(
            model_name='trip',
            name='shape',
            field=models.ForeignKey(blank=True, help_text='Shape used for this trip', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.shape'),
        ),
        migrations.CreateModel(
            name='ShapePoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', django.contrib.gis.db.models.fields.PointField(help_text='WGS 84 latitude/longitude of shape point', srid=4326)),
                ('sequence', models.IntegerField()),
                ('traveled', models.FloatField(blank=True, help_text='Distance of point from start of shape', null=True)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('shape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points', to='multigtfs.shape')),
            ],
            options={
                'db_table': 'shape_point',
            },
        ),
        migrations.CreateModel(
            name='Stop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_id', models.CharField(db_index=True, help_text='Unique identifier for a stop or station.', max_length=255)),
                ('code', models.CharField(blank=True, help_text='Uniquer identifier (short text or number) for passengers.', max_length=255)),
                ('name', models.CharField(help_text='Name of stop in local vernacular.', max_length=255)),
                ('desc', models.CharField(blank=True, help_text='Description of a stop.', max_length=255, verbose_name='description')),
                ('point', django.contrib.gis.db.models.fields.PointField(help_text='WGS 84 latitude/longitude of stop or station', srid=4326)),
                ('url', models.URLField(blank=True, help_text='URL for the stop')),
                ('location_type', models.CharField(blank=True, choices=[('0', 'Stop'), ('1', 'Station')], help_text='Is this a stop or station?', max_length=1)),
                ('timezone', models.CharField(blank=True, help_text='Timezone of the stop', max_length=255)),
                ('wheelchair_boarding', models.CharField(blank=True, choices=[('0', 'No information'), ('1', 'Some wheelchair boarding'), ('2', 'No wheelchair boarding')], help_text='Is wheelchair boarding possible?', max_length=1)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
                ('parent_station', models.ForeignKey(blank=True, help_text='The station associated with the stop', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.stop')),
            ],
            options={
                'db_table': 'stop',
            },
        ),
        migrations.CreateModel(
            name='StopTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrival_time', multigtfs.models.fields.seconds.SecondsField(blank=True, db_index=True, default=None, help_text='Arrival time. Must be set for end stops of trip.', null=True)),
                ('departure_time', multigtfs.models.fields.seconds.SecondsField(blank=True, default=None, help_text='Departure time. Must be set for end stops of trip.', null=True)),
                ('stop_sequence', models.IntegerField()),
                ('stop_headsign', models.CharField(blank=True, help_text='Sign text that identifies the stop for passengers', max_length=255)),
                ('pickup_type', models.CharField(blank=True, choices=[('0', 'Regularly scheduled pickup'), ('1', 'No pickup available'), ('2', 'Must phone agency to arrange pickup'), ('3', 'Must coordinate with driver to arrange pickup')], help_text='How passengers are picked up', max_length=1)),
                ('drop_off_type', models.CharField(blank=True, choices=[('0', 'Regularly scheduled drop off'), ('1', 'No drop off available'), ('2', 'Must phone agency to arrange drop off'), ('3', 'Must coordinate with driver to arrange drop off')], help_text='How passengers are picked up', max_length=1)),
                ('shape_dist_traveled', models.FloatField(blank=True, help_text='Distance of stop from start of shape', null=True, verbose_name='shape distance traveled')),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('stop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.stop')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.trip')),
            ],
            options={
                'db_table': 'stop_time',
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_type', models.IntegerField(blank=True, choices=[(0, 'Recommended transfer point'), (1, 'Timed transfer point (vehicle will wait)'), (2, 'min_transfer_time needed to successfully transfer'), (3, 'No transfers possible')], default=0, help_text='What kind of transfer?')),
                ('min_transfer_time', models.IntegerField(blank=True, help_text='How many seconds are required to transfer?', null=True)),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('from_stop', models.ForeignKey(help_text='Stop where a connection between routes begins.', on_delete=django.db.models.deletion.CASCADE, related_name='transfer_from_stop', to='multigtfs.stop')),
                ('to_stop', models.ForeignKey(help_text='Stop where a connection between routes ends.', on_delete=django.db.models.deletion.CASCADE, related_name='transfer_to_stop', to='multigtfs.stop')),
            ],
            options={
                'db_table': 'transfer',
            },
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_id', models.CharField(db_index=True, help_text='Unique identifier for a zone.', max_length=63)),
                ('feed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.feed')),
            ],
            options={
                'db_table': 'zone',
            },
        ),
        migrations.AddField(
            model_name='stop',
            name='zone',
            field=models.ForeignKey(blank=True, help_text='Fare zone for a stop ID.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.zone'),
        ),
        migrations.CreateModel(
            name='FareRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('extra_data', models.JSONField(blank=True, default=dict, null=True)),
                ('fare', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='multigtfs.fare')),
                ('route', models.ForeignKey(blank=True, help_text='Fare class is valid for this route.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='multigtfs.route')),
                ('contains', models.ForeignKey(blank=True, help_text='Fare class is valid for travel withing this zone.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fare_contains', to='multigtfs.zone')),
                ('destination', models.ForeignKey(blank=True, help_text='Fare class is valid for travel ending in this zone.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fare_destinations', to='multigtfs.zone')),
                ('origin', models.ForeignKey(blank=True, help_text='Fare class is valid for travel originating in this zone.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fare_origins', to='multigtfs.zone')),
            ],
            options={
                'db_table': 'fare_rules',
            },
        ),
    ]
