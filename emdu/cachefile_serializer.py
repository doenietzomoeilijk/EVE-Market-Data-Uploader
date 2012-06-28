"""
This module reads the cache files and serializes them into a Unified Uploader
format message.
"""

import datetime
from emds.data_structures import MarketOrderList, MarketOrder
from emds.formats.unified import encode_to_json
from emdu.rev_compat import blue

# Some constants that identify this uploader.
ORDER_GENERATOR = {
    "name": "EMDU", "key": "git"
}
UPLOAD_KEYS = [{
    "name": "EMDU", "key": "sexytime",
}]

def wintime_to_datetime(timestamp):
    """
    Given a funky Windows timestamp, convert it to a UTC datetime object.

    :param int timestamp: The timestamp, in win format.
    :rtype: datetime.datetime
    :returns: The correct UTC-aware timestamp.
    """

    return datetime.datetime.utcfromtimestamp((timestamp-116444736000000000)/10000000)

def serialize_orders(doc_dict):
    """
    Serializes a GetOrders cache file's contents.

    :param dict doc_dict: The parsed cache document in dict form.
    :rtype: str or None
    :returns: If
    """
    order_list = MarketOrderList(
        order_generator=ORDER_GENERATOR,
        upload_keys=UPLOAD_KEYS,
    )
    generated_at = datetime.datetime.now()

    for order_item in doc_dict['lret']:
        #print order_item
        for entry in order_item:
            #print entry
            order = MarketOrder(
                order_id=entry['orderID'],
                is_bid=entry['bid'],
                region_id=entry['regionID'],
                solar_system_id=entry['solarSystemID'],
                station_id=entry['stationID'],
                type_id=entry['typeID'],
                price=entry['price'],
                volume_entered=entry['volEntered'],
                volume_remaining=entry['volRemaining'],
                minimum_volume=entry['minVolume'],
                order_issue_date=wintime_to_datetime(entry['issueDate']),
                order_duration=entry['duration'],
                order_range=entry['range'],
                generated_at=generated_at,
            )
            order_list.add_order(order)

    if len(order_list) > 0:
        return encode_to_json(order_list)
    else:
        return None

def serialize_cache_file(cache_file_path):
    """
    Given a cache file, open it and determine whether it's something we can
    upload. If it is, serialize it to JSON, then return the serialized JSON.

    :param str cache_file_path: The full path to a cache file to read and
        potentially serialize.
    :rtype: str or None
    :returns: If the cache file contains something we can upload, return a
        JSON string that will be uploaded to EMDR. Otherwise, return None.
    """

    fobj = open(cache_file_path, 'r')
    # Parse with either reverence or despair.
    key, obj = blue.marshal.Load(fobj.read())

    print key[1]
    if key[1] == 'GetOrders':
        json_str = serialize_orders(obj)
        fobj.close()
        return json_str

    # This isn't a cache file we can do anything with. Oh bother.
    return None
