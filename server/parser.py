from typing import List
from lxml import etree
from datetime import datetime as dt
import os


CZPTTCISMessage = 'CZPTTCISMessage'
CZCanceledMessage = 'CZCanceledPTTMessage'

def parse_file(file) -> dict:
    with open(file) as f:
        xml = f.read()

    root = etree.fromstring(xml)

    if root.tag == CZCanceledMessage:
        return parse_CZCanceledMessage(root)
    elif root.tag == CZPTTCISMessage:
        return parse_CZPTTCISMessage(root)


def parse_CZPTTCISMessage(root) -> dict:
    msg = parse_identifiers(root.find('Identifiers'))
    msg['created'] = parse_creation(root)
    information = root.find('CZPTTInformation')
    msg['path'] = parse_locations(information)
    msg['calendar'] = parse_calendar(information)
    msg['networkSpecificParameters'] = network_specific_parameters(root)

    return msg

def parse_CZCanceledMessage(root) -> dict:
    msg = parse_identifiers(root)
    msg['created'] = parse_creation(root, "CZPTTCancelation")
    msg['calendar'] = parse_calendar(root)
    return msg


def str_to_datetime(date: str, format: str="%Y-%m-%dT%X"):
    return dt.strptime(date, format)

def parse_identifiers(identifiers_el) -> dict:
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

def parse_creation(root, element: str="CZPTTCreation"):
    created = root.find(element).text
    return str_to_datetime(created)

def parse_calendar(root) -> dict:
    calendar_d = {}
    calendar = root.find("PlannedCalendar")
    calendar_d['bitmap'] = calendar.find('BitmapDays').text
    calendar_d['startDate'] = str_to_datetime(calendar[1].find('StartDateTime').text)
    calendar_d['endDate'] = str_to_datetime(calendar[1].find('EndDateTime').text)
    return calendar_d

def network_specific_parameters(root) -> List:
    network_params = root.findall('NetworkSpecificParameter')
    params = []
    for param in network_params:
        params.append(etree.tostring(param))

    return params

def parse_location(parent) -> dict:
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

def parse_locations(element) -> List:
    location_info = element.findall('CZPTTLocation')
    locations = []

    for info in location_info:
        location_d = parse_location(info)
        timing = info.findall('.//Timing')
        for t in timing:
            key = ''
            if t.get('TimingQualifierCode').__eq__('ALA'):
                key = 'arrival'
            elif t.get('TimingQualifierCode').__eq__('ALD'):
                key = 'departure'
            location_d[key] = {'time': str_to_datetime(t.find('Time').text,"%H:%M:%S.0000000%z").timetz()}
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

        location_d['networkSpecificParameters'] = network_specific_parameters(info)
        locations.append(location_d)

    return locations
