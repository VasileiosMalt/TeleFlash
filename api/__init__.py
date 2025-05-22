# -*- coding: utf-8 -*-

# import Telethon API modules
from telethon import TelegramClient, types
from telethon.tl.functions.channels import GetChannelsRequest, GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetDiscussionMessageRequest, GetWebPageRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.stats import GetBroadcastStatsRequest


async def get_connection(session_file, api_id, api_hash, phone):
    """
    Get connection to Telegram API
    :param session_file:
    :param api_id:
    :param api_hash:
    :param phone:
    :return:
    """
    client = TelegramClient(session_file, api_id, api_hash)
    await client.connect()
    if await client.is_user_authorized():
        print('> Authorized!')
    else:
        print('> Not Authorized! Sending code request...')
        await client.send_code_request(phone)
        await client.sign_in(
            phone,
            input('Enter the code: ')
        )
    return client


async def get_entity_attrs(client: TelegramClient, source):
    """
    Get channel main attributes
    Source: entity (str | int | Peer | InputPeer)
    More on InputPeer: https://tl.telethon.dev/types/input_peer.html

    Reference:
        Telethon: https://docs.telethon.dev/en/latest/modules/client.html#telethon.client.users.UserMethods.get_entity
        Output attrs: https://core.telegram.org/constructor/channel
    """
    return await client.get_entity(source)


async def get_channel_req(client, source):
    """
    Get channel request
    Source: <ChannelInput>

    Reference:
        Telethon: https://tl.telethon.dev/methods/channels/get_channels.html
        Output attrs: https://core.telegram.org/constructor/chat
    """
    if type(source) != list:
        source = [source]

    return await client(
        GetChannelsRequest(source)
    )


async def full_channel_req(client, source):
    """
    Get full channel request
    Source: <ChannelInput>

    Reference:
        Telethon: https://tl.telethon.dev/methods/channels/get_full_channel.html
        Output attrs: https://core.telegram.org/constructor/messages.chatFull
    """

    return await client(
        GetFullChannelRequest(source)
    )


async def get_participants_request(client, source):
    """
    Get participants request
    :param client:
    :param source:
    :return:
    """
    return await client(
        GetParticipantsRequest(
            channel=source,
            filter=types.ChannelParticipantsRecent(),
            offset=1,
            limit=10,
            hash=0
        )
    )


async def get_posts(client, source, offset_date, min_id=0, offset_id=0):
    """
    get posts
    Source: entity (str | int | Peer | InputPeer)
        More on InputPeer: https://tl.telethon.dev/types/input_peer.html

    Reference:
        Telethon: https://tl.telethon.dev/methods/messages/get_history.html
        Output attrs: https://core.telegram.org/constructor/messages.channelMessages
    """

    return await client(
        GetHistoryRequest(
            peer=source,
            hash=0,
            limit=100,
            max_id=0,
            min_id=min_id,
            offset_id=offset_id,
            add_offset=0,
            offset_date=offset_date
        )
    )


async def get_discussion_message(client, source, msg_id):
    """
    Get discussion message
    Source: entity (str | int | Peer | InputPeer)
        More on InputPeer: https://tl.telethon.dev/types/input_peer.html
    msg_id: <message id>

    Reference:
        Telethon: https://tl.telethon.dev/methods/messages/get_discussion_message.html
        Output attrs: https://core.telegram.org/constructor/messages.discussionMessage
    """

    return await client(
        GetDiscussionMessageRequest(
            peer=source,
            msg_id=msg_id
        )
    )


async def get_web_page(client, url, webhash):
    """
    Get webpage
    :param client:
    :param url: <web url>
    :param webhash: <pagination> adding 0 by default.

    Reference:
        Telethon: https://tl.telethon.dev/methods/messages/get_web_page.html
        Output attrs: https://core.telegram.org/constructor/webPage
    """
    return await client(
        GetWebPageRequest(url, webhash)
    )


async def full_user_req(client, source, channel):
    """
    Get full user request
    Source: <InputUser>

    Reference:
        Telethon: https://tl.telethon.dev/methods/users/get_full_user.html
        Output attrs:
    """
    try:
        user = await client(
            GetFullUserRequest(source)
        )

        return user
    except ValueError:
        users = await client.get_participants(channel, aggressive=True)
        return users


async def photos_request(client, user_input):
    """
    Get user photos
    :param client:
    :param user_input:
    :return:
    """
    return await client(
        GetUserPhotosRequest(
            user_id=user_input,
            offset=0,
            max_id=0,
            limit=5
        )
    )


async def broadcast_stats_req(client, source):
    """
    Stats
    Source: <InputChannel>

    Reference:
        Telethon: https://tl.telethon.dev/methods/stats/get_broadcast_stats.html
        Output attrs: https://core.telegram.org/constructor/stats.broadcastStats
    """
    return await client(
        GetBroadcastStatsRequest(
            channel=source
        )
    )
