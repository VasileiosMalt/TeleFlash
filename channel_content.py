import pandas as pd
import asyncio
import time
from api import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tqdm import tqdm
from db.models import Channel, PostText
from dotenv import load_dotenv
import os
import logging
from datetime import datetime, timedelta

load_dotenv()

connection_string = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}"
engine = create_engine(connection_string)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info(f"Init program at {time.ctime()}")


sfile = os.getenv('SESSION_FILE')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')


def save_channel_data(channel_request, channel):
    logging.info("Saving channel data")
    full_channel_data = channel_request.to_dict()

    full_channel_data.pop('_', None)
    full_channel_data.pop('users', None)

    fields = ['id', 'about', 'participants_count', 'linked_chat_id', 'pts', 'pinned_msg_id']

    full_channel_data['full_chat'] = {k: i for k, i in full_channel_data['full_chat'].items() if k in fields}

    fields = ['id', 'title', 'username', 'date', 'fake']

    full_channel_data['chats'] = [
        {k: i for k, i in d.items() if k in fields} for d in full_channel_data['chats']
    ]
    full_channel_data = pd.DataFrame(full_channel_data['chats']) \
        .merge(pd.DataFrame([full_channel_data['full_chat']]), how='left')
    full_channel_data = full_channel_data.loc[full_channel_data['username'] == channel, :]
    full_channel_data = full_channel_data.loc[full_channel_data['participants_count'].notnull(), :]
    #full_channel_data = pd.DataFrame([full_channel_data['full_chat']])
    with Session(engine) as session:
        logging.info("Session started")
        for i, row in tqdm(full_channel_data.iterrows(), total=len(full_channel_data)):
            order = session.query(Channel).filter_by(id=row['id']).first()
            logging.debug(f"Processing channel ID: {row['id']}")
            if order is None:
                if row['username'] is not None:
                    logging.info(f"Adding new channel: {row['title']}")
                    order = Channel(
                        id=row['id'],
                        title=row['title'],
                        username=row['username'],
                        about=row['about'],
                        participants_count=row['participants_count'],
                        date=row['date'],
                        fake=row['fake'],
                        pts=row['pts'],
                        pinned_msg_id=row['pinned_msg_id'],
                        linked_chat_id=row['linked_chat_id']
                    )
                    session.add(order)
                    session.commit()
            else:
                logging.info(f"Updating existing channel: {row['title']}")
                order.title = row['title']
                order.username = row['username']
                order.about = row['about']
                order.participants_count = row['participants_count']
                order.date = row['date']
                order.fake = row['fake']
                order.pts = row['pts']
                order.pinned_msg_id = row['pinned_msg_id']
                order.linked_chat_id = row['linked_chat_id']
                session.commit()


def download_channel(channels: list) -> None:
    # event loop
    loop = asyncio.get_event_loop()
    logging.info("Event loop created")

    # Get `client` connection
    client = loop.run_until_complete(
        get_connection(sfile, api_id, api_hash, phone)
    )
    logging.info("Client connection established")

    # iterate channels
    for channel in channels:
        logging.info(f"Processing channel: {channel}")
        try:
            # Channel's attributes
            entity_attrs = loop.run_until_complete(get_entity_attrs(client, channel))
            logging.debug(f"Entity attributes: {entity_attrs}")

            # Get Channel ID | convert output to dict
            channel_id = entity_attrs.id

            # Collect Source -> GetFullChannelRequest
            channel_request = loop.run_until_complete(full_channel_req(client, channel_id))

            save_channel_data(channel_request, channel)
            yesterday = datetime.now() - timedelta(days=0)
            # Collect posts
            posts = loop.run_until_complete(get_posts(client, channel_id, offset_date=yesterday))  # , min_id=date
            logging.info(f"Collected posts for channel ID: {channel_id}")

            data = posts.to_dict()

            logging.info(f"Collected posts count: {len(data['messages'])}")

            df = pd.DataFrame(data['messages'])
            df = df.loc[df['_'] == "Message",]
            df.media = df.media.str['_']
            df.peer_id = df.peer_id.str['channel_id'].astype('Int64')
            df.reply_to = df.reply_to.str['reply_to_msg_id'].astype('Int64')
            if df.replies.isna().mean() < 1:
                df.replies = df.replies.str['channel_id'].astype('Int64')

            if df.fwd_from.isna().mean() < 1:
                df['fwd_from_channel_id'] = df.fwd_from.str['from_id'].str['channel_id'].astype('Int64')
                df['fwd_from_channel_post'] = df.fwd_from.str['channel_post'].astype('Int64')

            df.entities = df.entities.apply(lambda x: [i.get('url') for i in x if i.get('url')])

            df = df.drop(['ttl_period', 'action', 'via_bot_id', 'restriction_reason', 'reply_markup', '_',
                          'out', 'media_unread', 'silent', 'post', 'pinned', 'from_scheduled', 'fwd_from',
                          'grouped_id', 'legacy', 'edit_hide', 'mentioned', 'post_author', 'from_id'], axis=1, errors='ignore')

            post_texts = df.loc[df['message'].notnull(), ['id', 'peer_id', 'date', 'message', 'views', 'forwards',
                                                          'edit_date']].reset_index(drop=True)
            post_entities = df.loc[df['entities'].notnull(), ['id', 'peer_id', 'entities']].explode('entities')
            post_entities = post_entities.loc[post_entities['entities'].notnull(), :].reset_index(drop=True)
            fields = ['id', 'title', 'username', 'date', 'fake']
            chats = pd.DataFrame(data['chats'])[fields]
            with Session(engine) as session:
                logging.info("Session started for saving posts and chats")
                for i, row in tqdm(chats.iterrows(), total=len(chats)):
                    order = session.query(Channel).filter_by(id=row['id']).first()
                    if order is None:
                        if pd.isna(row['username']) is False:
                            order = Channel(
                                id=row['id'],
                                title=row['title'],
                                username=row['username'],
                                date=row['date'],
                                fake=row['fake']
                            )
                            session.add(order)
                            session.commit()
                    else:
                        pass

                for i, row in tqdm(post_texts.iterrows(), total=len(post_texts)):
                    order = session.query(PostText).filter_by(id=row['id'],
                                                               peer_id=row['peer_id']).first()
                    if order is None:
                        order = PostText(
                            id=row['id'],
                            peer_id=row['peer_id'],
                            date=row['date'],
                            message=row['message'],
                            views=row['views'],
                            forwards=row['forwards']
                        )
                        session.add(order)
                        session.commit()
                    else:
                        pass


            post_entities.to_sql('post_entities', engine, if_exists='append', index=False)

            # sleep program for a few seconds
            if len(channels) > 1:
                logging.info("Sleeping for 60 seconds")
                time.sleep(60)
        except Exception as e:
            logging.error(f"Error processing channel {channel}: {e}")
            logging.info(f"Failed channel: {channel}")

    logging.info(f"End program at {time.ctime()}")


if __name__ == '__main__':
    channels = ['severnygorod', 'agapov_fi', 'karaulny', 'rusbrief', 'octgnews', 'tass_agency', 'baltnews', 'fontankaspb', 'dprunews', 'sp_1703', 'glavmedia', 'houseofcardseurope', 'good78news', 'rian_ru', 'belta_telegramm', 'radiogovoritmsk', 'bbbreaking', 'paperpaper_ru', 'nevnov', 'swodki', 'vzglyad_ru', 'parstodayrussian', 'ukraina_ru', 'solovievlive', 'rossiyaneevropa', 'online47news', 'riafan', 'radiomirby', 'dirtytatarstan', 'rgrunews', 'inosmichannel', 'sputnikby', 'rbc_news', 'ssigny', 'boyart777', 'lentadnya', 'radiosvoboda', 'kommersant', 'topspb_tv', 'allnews47', 'rt_russian', 'absatzmedia', 'match_tv', 'truekpru', 'bbcrussian', 'houseofcardsrussia', 'OdessaRussi', 'Novoeizdanie', 'rus_demiurge', 'stranaua', 'rbc_brief', 'aifonline', 'ostashkonews', 'dimsmirnov175', 'ateobreaking', 'infantmilitario', 'UAnotRU', 'smotri_media', 'thehandofthekremlin', 'leningrad_guide', 'izvestia', 'meduzalive', 'highlylikely20', 'rentv_news', 'znua_live', 'atn_btrc', 'vestiru24', 'chvkmedia', 'espresotb', 'kshulika', 'orientsouthrus', 'dwglavnoe', 'ZOVcrimea', 'Belarus_VPO', 'readovkanews', 'ranarod', 'gazetaru', 'nexta_live', 'ntvnews', 'uniannet', 'lady_north', 'fuckyouthatswhy', 'nstarikovru', 'new_militarycolumnist', 'mk_ru', 'lab365', 'go338', 'postovo', 'asphaltt', 'politkraina', 'rlz_the_kraken', 'ru2ch', 'bfmnews', 'russtrat', 'tv360', 'radio_sputnik', 'minut30', 'pluanews', 'rtvinews', 'interfaxonline', 'istorijaoruzijaz', 'currenttime', 'sputniklive', 'newsgrpua', 'srochnow', 'ukrpravda_news', 'first_political', 'oldlentach', 'RUSanctions', 'Pravda_Gerashchenko', 'warhistoryalconafter', 'ivan_utenkov13', 'TCH_channel', 'the_moscow_post', 'UkraineNow', 'openukraine', 'ukr_shvydko', 'lentachold', 'huyovy_kharkiv', 'kontext_channel', 'russica2', 'tvrain', 'operativnozsu', 'rus_now_news', 'voynareal', 'lachentyt', 'russianonwars', 'dmytrogordon_official', 'banksta', 'TolkoPoDely', 'rybar', 'rhymestg', 'ragnarockkyiv', 'ukraina24tv', 'bankrollo', 'truexanewsua', 'sheyhtamir1974', 'aleksandrsemchenko', 'tsaplienko', 'varlamov_news', 'DavydovIn', 'boris_rozhin', 'RVvoenkor', 'redacted6', 'zerkalo_io', 'voenacher', 'Mikle1On', 'UaOnlii', 'vchkogpu', 'kaktovottak', 'novosti_efir', 'shot_shot', 'insiderUKR', 'slavaded1337', 'bloodysx', 'breakingmash', 'readovkaru', 'ostorozhno_novosti', 'okoo_ukr', 'Cbpub', 'warfakes', 'montyan2', 'moscowmap', 'asupersharij', 'nevzorovtv', 'V_Zelenskiy_official', 'yurasumy']

    download_channel(channels)
