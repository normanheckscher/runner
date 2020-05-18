#!/usr/bin/env python

import fitparse, os

def dump_date(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

class DumperNotFoundError(RuntimeError):
    pass

class GPXDumper:
    TAB = '  '

    def dump(self, activity):
        buffer = []

        buffer.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        buffer.append(self._dump_training_database(activity))

        return ''.join(buffer)

    def dump_to_file(self, activity, filename):
        open(filename, 'w').write(self.dump(activity))

    def _dump_training_database(self, activity):
        buffer = []

        buffer.append("""<gpx version="1.1" creator="runner" xsi:schemaLocation="http://www.topografix.com/GPX/1/1
                                http://www.topografix.com/GPX/1/1/gpx.xsd
                                http://www.garmin.com/xmlschemas/GpxExtensions/v3
                                http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd
                                http://www.garmin.com/xmlschemas/TrackPointExtension/v1
                                http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd"
    xmlns="http://www.topografix.com/GPX/1/1"
    xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1"
    xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
""")

        buffer.append(self._dump_metadata(activity))
        buffer.append(self._dump_activity(activity))
        buffer.append('</gpx>')

        return ''.join(buffer)

    def _dump_metadata(self, activity):
        buffer = []

        buffer.append(self.TAB + '<metadata>\n')
        buffer.append(2*self.TAB + '<time>%s</time>\n' % dump_date(activity.identifier))
        buffer.append(self.TAB + '</metadata>\n')

        return ''.join(buffer)

    def _dump_activity(self, activity):
        buffer = []

        for lap in activity.laps:
            buffer.append(self._dump_lap(lap))

        return ''.join(buffer)

    def _dump_lap(self, lap):
        buffer = []

        buffer.append(self.TAB + '<trk>\n')
        buffer.append(2*self.TAB + '<trkseg>\n')

        for trackpoint in lap.trackpoints:
            buffer.append(self._dump_trackpoint(trackpoint))

        buffer.append(2*self.TAB + '</trkseg>\n')
        buffer.append(self.TAB + '</trk>\n')

        return ''.join(buffer)

    def _dump_trackpoint(self, trackpoint):
        buffer = []

        attrs = '' if trackpoint.position is None else ' lat="%.16f" lon="%.16f"' % (trackpoint.position.latitude, trackpoint.position.longitude)

        buffer.append(3*self.TAB + '<trkpt%s>\n' % attrs)
        buffer.append(4*self.TAB + '<time>%s</time>\n' % dump_date(trackpoint.time))
        buffer.append(4*self.TAB + '<ele>%d</ele>\n' % trackpoint.altitude)
        buffer.append(4*self.TAB + '<gpxtpx:TrackPointExtension>\n')
        buffer.append(5*self.TAB + '<gpxtpx:hr>%d</gpxtpx:hr>\n' % trackpoint.heart_rate)
        buffer.append(4*self.TAB + '</gpxtpx:TrackPointExtension>\n')
        buffer.append(3*self.TAB + '</trkpt>\n')

        return ''.join(buffer)

class TCXDumper:
    TAB = '  '

    def dump(self, activity):
        buffer = []

        buffer.append('<?xml version="1.0" encoding="UTF-8"?>\n')
        buffer.append(self._dump_training_database(activity))

        return ''.join(buffer)

    def dump_to_file(self, activity, filename):
        open(filename, 'w').write(self.dump(activity))

    def _dump_training_database(self, activity):
        buffer = []

        buffer.append("""<TrainingCenterDatabase
    xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
    xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
    xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
    xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
""")

        buffer.append(self._dump_activities(activity))
        buffer.append('</TrainingCenterDatabase>')

        return ''.join(buffer)

    def _dump_activities(self, activity):
        buffer = []

        buffer.append(self.TAB + '<Activities>\n')

        buffer.append(self._dump_activity(activity))

        buffer.append(self.TAB + '</Activities>\n')

        return ''.join(buffer)

    def _dump_activity(self, activity):
        buffer = []

        buffer.append(2*self.TAB + '<Activity Sport="%s">\n' % "Running" if activity.type is None else activity.type)
        buffer.append(3*self.TAB + '<Id>%s</Id>\n' % dump_date(activity.identifier))
        for lap in activity.laps:
            buffer.append(self._dump_lap(lap))
        buffer.append(2*self.TAB + '</Activity>\n')

        return ''.join(buffer)

    def _dump_lap(self, lap):
        buffer = []

        buffer.append(3*self.TAB + '<Lap StartTime="%s">\n' % dump_date(lap.start_time))
        buffer.append(4*self.TAB + '<TotalTimeSeconds>%d</TotalTimeSeconds>\n' % lap.duration)
        buffer.append(4*self.TAB + '<DistanceMeters>%d</DistanceMeters>\n' % lap.distance)
        buffer.append(4*self.TAB + '<Calories>%d</Calories>\n' % lap.calories)
        buffer.append(4*self.TAB + '<MaximumSpeed>%f</MaximumSpeed>\n' % lap.max_speed)
        buffer.append(4*self.TAB + '<AverageHeartRateBpm><Value>%d</Value></AverageHeartRateBpm>\n' % lap.avg_heart_rate)
        buffer.append(4*self.TAB + '<MaximumHeartRateBpm><Value>%d</Value></MaximumHeartRateBpm>\n' % lap.max_heart_rate)
        if lap.trigger_method is not None:
            buffer.append(4*self.TAB + '<TriggerMethod>%s</TriggerMethod>\n' % lap.trigger_method)

        buffer.append(4*self.TAB + '<Track>\n')
        for trackpoint in lap.trackpoints:
            buffer.append(self._dump_trackpoint(trackpoint))
        buffer.append(4*self.TAB + '</Track>\n')

        buffer.append(3*self.TAB + '</Lap>\n')

        return ''.join(buffer)

    def _dump_trackpoint(self, trackpoint):
        buffer = []

        buffer.append(5*self.TAB + '<Trackpoint>\n')
        buffer.append(6*self.TAB + '<Time>%s</Time>\n' % dump_date(trackpoint.time))
        buffer.append(6*self.TAB + '<DistanceMeters>%d</DistanceMeters>\n' % trackpoint.distance)
        buffer.append(6*self.TAB + '<AltitudeMeters>%d</AltitudeMeters>\n' % trackpoint.altitude)
        buffer.append(6*self.TAB + '<HeartRateBpm><Value>%d</Value></HeartRateBpm>\n' % trackpoint.heart_rate)

        if trackpoint.position is not None:
            buffer.append(self._dump_position(trackpoint.position))

        buffer.append(5*self.TAB + '</Trackpoint>\n')

        return ''.join(buffer)

    def _dump_position(self, position):
        buffer = []

        buffer.append(6*self.TAB + '<Position>\n')
        buffer.append(7*self.TAB + '<LatitudeDegrees>%.16f</LatitudeDegrees>\n' % position.latitude)
        buffer.append(7*self.TAB + '<LongitudeDegrees>%.16f</LongitudeDegrees>\n' % position.longitude)
        buffer.append(6*self.TAB + '</Position>\n')

        return ''.join(buffer)

class FITDumper:
    def dump(self, fit_file):
        fitfile = fitparse.FitFile(
            fit_file,
            data_processor=fitparse.StandardUnitsDataProcessor(),
        )
        activity = model.Activity()
        data = {}

        for message in fitfile.get_messages():
            self._handle_message(message, activity, data)

        return activity

    def _handle_message(self, message, activity, data):
        if message.name == 'activity':
            data['trigger_method'] = message.get('type').value
        elif message.name == 'lap':
            self._handle_lap(message, activity, data)
        elif message.name == 'record':
            self._handle_record(message, activity, data)

    def _handle_lap(self, message, activity, data):
        lap = model.Lap(message.get('start_time').value)

        lap.trigger_method = data['trigger_method']
        lap.duration = int(self._get_or_else(message, 'total_elapsed_time', 0))
        lap.distance = int(self._get_or_else(message, 'total_distance', 0))
        lap.calories = int(self._get_or_else(message, 'total_calories', 0))
        lap.max_speed = float(self._get_or_else(message, 'max_speed', 0))
        lap.avg_heart_rate = int(self._get_or_else(message, 'avg_heart_rate', 0))
        lap.max_heart_rate = int(self._get_or_else(message, 'max_heart_rate', 0))

        activity.type = message.get('sport').value
        activity.laps.append(lap)

    def _handle_record(self, message, activity, data):
        trackpoint = model.Trackpoint(message.get('timestamp').value)

        trackpoint.heart_rate = int(self._get_or_else(message, 'heart_rate', 0))

        activity.laps[-1].trackpoints.append(trackpoint)

    def _get_or_else(self, message, key, default=None):
        value = message.get(key)

        return value.value if value is not None and value.value is not None else default

def dumper_for_file(filename):
    parsers_map = {
        'fit': FITDumper, # may crash as not implemented yet
        'tcx': TCXDumper,
        'gpx': GPXDumper
    }

    _, extension = os.path.splitext(filename)
    extension = extension[1:] # remove the leading '.'

    try:
        return parsers_map[extension]()
    except KeyError:
        raise DumperNotFoundError('Not dumper for extension: ' + extension)

def dump_to_file(activity, filename):
    dumper = dumper_for_file(filename)

    return dumper.dump_to_file(activity, filename)
