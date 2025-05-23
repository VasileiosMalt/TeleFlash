# -*- coding: utf-8 -*-

# Import modules
import pandas as pd
import asyncio
import json
import os

# import submodules
from configparser import ConfigParser
from urllib.parse import urlparse
from datetime import datetime

# Import Telegram API submodules
from api import full_channel_req

'''
Creating functions
'''


# Get config attrs
def get_config_attrs(path: str = './config/config.ini') -> dict:
    """
    Get config attrs
    :param path: path to config file
    :return:
    """
    # config parser
    config = ConfigParser()
    config.read(path)

    # Telegram API credentials
    attrs = config['Telegram API credentials']
    return dict(attrs)


# event loop
loop = asyncio.get_event_loop()

'''

JSON Encoder

'''


def cmd_request_type(args):
    """
    Get user-console request
    :param args:
    :return:
    """
    tm_channel = args['telegram_channel']
    batch_file = args['batch_file']

    req_type = 'channel' if tm_channel is not None else 'batch'
    req_input = tm_channel if tm_channel is not None else batch_file

    return req_type, req_input


def process_participants_count(client, channel_id):
    """
    Process collected chats

    :return: participants count
    """
    channel_request = loop.run_until_complete(
        full_channel_req(client, channel_id)
    )

    return channel_request.full_chat.participants_count


def write_collected_chats(
        chats_object,
        file,
        source,
        counter,
        req_type,
        client,
        output_folder
):
    """
    Write collected chats
    :param chats_object: chats metadata from API requests
    :param file: a txt file to write chats' data (id, username)
    :param source: channel requested by the user through cmd
    :param counter: dict object to count mentioned channels
    :param req_type: request type (channel request or from messages)
    :param client: Telegram API client
    :param output_folder: Folder to save collected data
    """
    metadata = []
    for c in chats_object:
        try:
            id_ = c['id']
            username = c['username']
            if username is not None:
                file.write(f'{id_}\n')

                # collect metadata
                if id_ in counter.keys():
                    counter[id_]['counter'] += 1
                    counter[id_][req_type] += 1
                    src = counter[id_]['source']
                    if source not in src:
                        counter[id_]['source'].append(source)
                else:
                    counter[id_] = {
                        'username': username,
                        'counter': 1,
                        'from_messages': 1 if req_type == 'from_messages' else 0,
                        'channel_request': 1 if req_type == 'channel_request' else 0,
                        'channel_req_targeted_by': {
                            'channels': ['self']
                        },
                        'source': [source]
                    }

                    # Telegram API -> full channel request
                    try:
                        channel_request = loop.run_until_complete(
                            full_channel_req(client, id_)
                        )

                        channel_request = channel_request.to_dict()
                        collected_chats = channel_request['chats']

                        for ch in collected_chats:
                            if ch['id'] == channel_request['full_chat']['id']:
                                ch['participants_count'] = \
                                    channel_request['full_chat']['participants_count']
                            else:
                                ch_id = ch['id']
                                try:
                                    ch['participants_count'] = \
                                        process_participants_count(client, ch_id)
                                except TypeError:
                                    ch['participants_count'] = 0

                                # write new id
                                if ch['username'] is not None:
                                    file.write(f'{ch_id}\n')

                                    # process in counter
                                    if ch_id in counter.keys():
                                        counter[ch_id]['counter'] += 1
                                        counter[ch_id]['channel_request'] += 1
                                        counter[ch_id]['channel_request_targeted_by']['channels'].append(username)
                                    else:
                                        counter[ch_id] = {
                                            'username': ch['username'],
                                            'counter': 1,
                                            'from_messages': 0,
                                            'channel_request': 1,
                                            'channel_req_targeted_by': {
                                                'channels': [username]
                                            },
                                            'source': [source]
                                        }

                        metadata.extend(
                            [
                                i for i in collected_chats
                                if i['username'] is not None
                            ]
                        )
                    except ValueError:
                        # Save exceptions to new file
                        exceptions_path = f'{output_folder}/user_exceptions.txt'
                        w = open(exceptions_path, encoding='utf-8', mode='a')
                        w.write(f'ID - {id_}\n')
                        w.close()

        except KeyError:
            pass

    df = pd.DataFrame(metadata)
    csv_path = f'{output_folder}/collected_chats.csv'
    df.to_csv(
        csv_path,
        encoding='utf-8',
        mode='a',
        index=False,
        header=not os.path.isfile(csv_path)
    )

    return counter


def timestamp_attrs(data, col='date'):
    """
    Time - date attributes
    :param data:
    :param col:
    :return:
    """
    t = pd.to_datetime(
        data[col],
        infer_datetime_format=True,
        yearfirst=True
    )

    # timestamp attributes
    data[f'{col}'] = t.dt.strftime('%Y-%m-%d %H:%M:%S')
    data[f'{col}_string'] = t.dt.strftime('%Y-%m-%d')
    data[f'{col}_year'] = t.dt.year
    data[f'{col}_month_name'] = t.dt.month_name()
    data[f'{col}_day'] = t.dt.day
    data[f'{col}_day_name'] = t.dt.day_name()
    data[f'{col}_time_hour'] = t.dt.strftime('%H:%M:%S')
    data[f'{col}_quarter'] = t.dt.quarter
    data[f'{col}_dayofyear'] = t.dt.dayofyear
    data[f'{col}_weekofyear'] = t.dt.isocalendar().week

    return data


def clean_msg(text):
    """
    Clean msg
    :param text:
    :return:
    """
    return ' '.join(text.split()).strip()


def msg_attrs(msg, res):
    """
    Message attributes
    :param msg: message object
    :param res: dict object to store message attributes
    :return: dict object with message attributes
    """
    t = msg['from_id']
    if t is not None:
        t = t['_']

    # parser
    parser = {
        'PeerChannel': 'channel_id',
        'PeerUser': 'user_id'
    }

    try:
        id_key = parser[t]
        from_id = msg['from_id'][id_key]

        res['msg_from_peer'] = t
        res['msg_from_id'] = from_id
    except KeyError:
        pass

    return res


def get_channel_name(channel_id, channels):
    """
    Get channel name
    :param channel_id:
    :param channels:
    :return:
    """
    channel_name = None
    try:
        channel_name = channels[
            channels['id'] == channel_id
            ]['username'].iloc[0]
    except IndexError:
        pass

    return channel_name


def get_forward_attrs(msg, res, channels_data):
    """
    Get forward attrs
    :param msg:
    :param res:
    :param channels_data:
    :return:
    """
    date = msg['date']
    msg_id = msg['channel_post']

    # get from id value
    from_id = msg['from_id']
    if from_id:
        channel_id = from_id['channel_id']
        channel_name = get_channel_name(channel_id, channels_data)
    else:
        channel_id = None
        channel_name = None

    # process dates
    t = pd.to_datetime(
        date,
        infer_datetime_format=True,
        yearfirst=True
    )

    date = t.strftime('%Y-%m-%d %H:%M:%S')
    date_string = t.strftime('%Y-%m-%d')

    res['forward_msg_date'] = date
    res['forward_msg_date_string'] = date_string
    res['from_channel_id'] = channel_id
    res['from_channel_name'] = channel_name

    if channel_name:
        n = channel_name
        res['forward_msg_link'] = f'https://t.me/{n}/{msg_id}'

    return res


def get_reply_attrs(msg, res, username):
    """
    Get reply attrs
    :param msg:
    :param res:
    :param username:
    :return:
    """
    reply = msg['reply_to']
    reply_to_msg_id = None
    reply_msg_link = None
    is_reply = 0
    if reply:
        is_reply = 1
        reply_to_msg_id = msg['reply_to_msg_id']
        reply_msg_link = f'https://t.me/{username}/{reply_to_msg_id}'

    res['is_reply'] = is_reply
    res['reply_to_msg_id'] = reply_to_msg_id
    res['reply_msg_link'] = reply_msg_link

    return res


def get_netloc(value):
    """
    Get URL domains < netloc >
    :param value:
    :return:
    """
    n = urlparse(value).netloc
    return n.replace('www.', '')


def get_url_attrs(media, res):
    """
    Get URL attrs
    :param media:
    :param res:
    :return:
    """
    has_url = 0
    url = None
    domain = None
    url_title = None
    url_description = None
    if res['media_type'] == 'MessageMediaWebPage':
        url = media['webpage']['url']
        if url:
            has_url = 1

            # get domain
            domain = get_netloc(url)

            # title
            url_title = media['webpage']['title']
            url_description = media['webpage']['description']

    res['has_url'] = has_url
    res['url'] = url
    res['domain'] = domain
    res['url_title'] = url_title
    res['url_description'] = url_description

    return res


def get_document_attrs(media, res):
    """
    Get document attrs
    :param media:
    :param res:
    :return:
    """
    document_type = None
    video_duration = None
    if res['media_type'] == 'MessageMediaDocument':
        document_type = media['document']['mime_type']

        # get duration
        attrs = media['document']['attributes']
        for i in attrs:
            if i['_'] == 'DocumentAttributeVideo':
                video_duration = i['duration']
                break

    return document_type, video_duration


def get_poll_attrs(media, res):
    """
    Get poll attrs
    :param media:
    :param res:
    :return:
    """
    poll_question = None
    poll_number_results = None
    if res['media_type'] == 'MessageMediaPoll':
        poll_question = media['poll']['question']
        poll_number_results = len(media['results'])

    return poll_question, poll_number_results


def get_contact_attrs(media, res):
    """
    Get contact attrs
    :param media:
    :param res:
    :return:
    """
    contact_phone_number = None
    contact_name = None
    contact_userid = None
    if res['media_type'] == 'MessageMediaContact':
        contact_phone_number = media['phone_number']
        contact_name = media['first_name'] + ' ' + media['last_name']
        contact_userid = media['user_id']

    return contact_phone_number, contact_name, contact_userid


def get_geo_attrs(media, res):
    """
    Get geo attrs
    :param media:
    :param res:
    :return:
    """
    lat = None
    lng = None
    title = None
    address = None
    if res['media_type'] in ['MessageMediaGeo', 'MessageMediaVenue']:
        lat = media['geo']['lat']
        lng = media['geo']['lng']

        if 'title' in media.keys():
            title = media['title']
            address = media['address']

    res['geo_shared_lat'] = lat
    res['geo_shared_lng'] = lng
    res['geo_shared_title'] = title
    res['geo_shared_address'] = address

    return res


def chats_dataset_columns():
    """
    Chats dataset -> columns
    """
    return [
        '_',
        'id',
        'username',
        'title',
        'date',
        'left',
        'broadcast',
        'verified',
        'megagroup',
        'restricted',
        'signatures',
        'min',
        'scam',
        'has_link',
        'has_geo',
        'slowmode_enabled',
        'call_active',
        'call_not_empty',
        'fake',
        'gigagroup',
        'restriction_reason',
        'admin_rights',
        'banned_rights',
        'default_banned_rights',
        'participants_count',
        'collected_actions',
        'collected_posts',
        'replies',
        'other_actions',
        'number_views',
        'forwards',
        'replies_received'
    ]


def msgs_dataset_columns():
    """
    Msgs dataset -> columns
    :return:
    """
    return [
        'signature',
        'channel_id',
        'username',
        'message',
        'date',
        'date_string',
        'date_year',
        'date_month_name',
        'date_day',
        'date_day_name',
        'date_time_hour',
        'date_quarter',
        'date_dayofyear',
        'date_weekofyear',
        'msg_link',
        'msg_from_peer',
        'msg_from_id',
        'views',
        'number_replies',
        'number_forwards',
        'is_forward',
        'forward_msg_date',
        'forward_msg_date_string',
        'from_channel_id',
        'from_channel_name',
        'forward_msg_link',
        'is_reply',
        'reply_to_msg_id',
        'reply_msg_link',
        'contains_media',
        'media_type',
        'has_url',
        'url',
        'domain',
        'url_title',
        'url_description',
        'document_type',
        'video_duration_secs',
        'poll_question',
        'poll_number_results',
        'contact_phone_number',
        'contact_name',
        'contact_userid',
        'geo_shared_lat',
        'geo_shared_lng',
        'geo_shared_title',
        'geo_shared_address'
    ]


'''
Network
'''


def normalize_values(data):
    """
    :param data: a list of tuples -> based on G.degree
    """
    max_v = max([v for i, v in data])
    min_v = min([v for i, v in data])

    return [
        int((i - min_v) / (max_v - min_v) * 450) + 50
        for _, i in data
    ]
