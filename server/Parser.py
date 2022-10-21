from typing import List
from lxml import etree
from datetime import datetime as dt
from MSG_TYPES_ENUM import MSGTYPE

class Parser:
    CZPTTCISMessage = 'CZPTTCISMessage'
    CZCanceledMessage = 'CZCanceledPTTMessage'

    def __init__(self):
        self.msg_type = None

    def parse_file(self, file: str) -> dict:
        with open(file) as f:
            xml = f.read()

        root = etree.fromstring(xml)

        if root.tag == self.CZCanceledMessage:
            self.msg_type = MSGTYPE.CANCELED
            return self.parse_CZCanceledMessage(root)
        elif root.tag == self.CZPTTCISMessage:
            related_id = root.find('.//RelatedPlannedTransportIdentifiers')
            if related_id is None:
                self.msg_type = MSGTYPE.PLANNED
            else:
                self.msg_type = MSGTYPE.REROUTE
            return self.parse_CZPTTCISMessage(root)

    def parse_CZPTTCISMessage(self, root) -> dict:
        msg = self.parse_identifiers(root.find('Identifiers'))
        msg['created'] = self.parse_creation(root)
        information = root.find('CZPTTInformation')
        msg['path'] = self.parse_locations(information)
        msg['calendar'] = self.parse_calendar(information)
        msg['networkSpecificParameters'] = self.network_specific_parameters(root)

        return msg

    def parse_CZCanceledMessage(self, root) -> dict:
        msg = self.parse_identifiers(root)
        msg['created'] = self.parse_creation(root, "CZPTTCancelation")
        msg['calendar'] = self.parse_calendar(root)
        return msg

    @staticmethod
    def str_to_datetime(date: str, format: str = "%Y-%m-%dT%X"):
        return dt.strptime(date, format)

    def parse_identifiers(self, identifiers_el) -> dict:
        obj = {}
        for child in identifiers_el:
            if child.tag == 'PlannedTransportIdentifiers':
                if child[0].text == 'PA':
                    obj['PAID'] = child.find('Core').text,
                elif child[0].text == 'TR':
                    obj['TRID'] = child.find('Core').text,
                obj[child[0].text] = {
                    'Company': child.find('Company').text,
                    'Variant': int(child.find('Variant').text),
                    'Year': int(child.find('TimetableYear').text)}
            elif child.tag == 'RelatedPlannedTransportIdentifiers':
                obj['plannedPAID'] = {
                    'ID': child.find('Core').text,
                    'Company': child.find('Company').text,
                    'Variant': int(child.find('Variant').text),
                    'Year': int(child.find('TimetableYear').text)}
        return obj

    def parse_creation(self, root, element: str = "CZPTTCreation"):
        created = root.find(element).text
        return self.str_to_datetime(created)

    def parse_calendar(self, root) -> dict:
        calendar_d = {}
        calendar = root.find("PlannedCalendar")
        calendar_d['bitmap'] = calendar.find('BitmapDays').text
        calendar_d['startDate'] = self.str_to_datetime(calendar[1].find('StartDateTime').text)
        calendar_d['endDate'] = self.str_to_datetime(calendar[1].find('EndDateTime').text)
        return calendar_d

    def network_specific_parameters(self, root) -> List:
        network_params = root.findall('NetworkSpecificParameter')
        params = []
        for param in network_params:
            params.append(etree.tostring(param))

        return params

    def parse_location(self, parent) -> dict:
        location = parent.findall('Location')
        location_d = {}
        for loc in location:
            location_d['country'] = loc.find('CountryCodeISO').text
            location_d['locationCode'] = loc.find('LocationPrimaryCode').text
            location_d['name'] = loc.find('PrimaryLocationName').text
            try:
                location_d['subsidiaryIdentification'] = etree.tostring(loc.find('LocationSubsidiaryIdentification'))
            except TypeError:
                location_d['subsidiaryIdentification'] = ''
        return location_d

    def parse_locations(self, element) -> List:
        location_info = element.findall('CZPTTLocation')
        locations = []

        for info in location_info:
            location_d = self.parse_location(info)
            timing = info.findall('.//Timing')
            for t in timing:
                key = ''
                if t.get('TimingQualifierCode').__eq__('ALA'):
                    key = 'arrival'
                elif t.get('TimingQualifierCode').__eq__('ALD'):
                    key = 'departure'
                location_d[key] = {'time': self.str_to_datetime(t.find('Time').text, "%H:%M:%S.0000000%z")}
            location_d['Responsible'] = {'responsibleRU': None,
                                         'responsibleIM': None}
            try:
                location_d['Responsible']['responsibleRU'] = int(info.find('ResponsibleRU').text)
            except AttributeError:
                pass

            try:
                location_d['Responsible']['responsibleIM'] = int(info.find('ResponsibleIM').text)
            except AttributeError:
                pass

            try:
                location_d['trainType'] = int(info.find('TrainType').text)
            except AttributeError:
                location_d['trainType'] = None

            location_d['traffic'] = {'trafficType': None,
                                     'commercialTrafficType': None}
            try:
                location_d['traffic']['trafficType'] = info.find('TrafficType').text
            except AttributeError:
                pass

            try:
                location_d['commercialTrafficType']: int(info.find('CommercialTrafficType').text)
            except AttributeError:
                pass

            train_activity = info.findall('TrainActivity')
            location_d['trainActivity'] = []
            for activity in train_activity:
                location_d['trainActivity'].append(activity.find('TrainActivityType').text)

            try:
                location_d['operationalTrainNumber'] = int(info.find('OperationalTrainNumber').text)
            except AttributeError:
                location_d['operationalTrainNumber'] = None

            location_d['networkSpecificParameters'] = self.network_specific_parameters(info)
            locations.append(location_d)

        return locations
