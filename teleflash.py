#!/usr/bin/env python
# coding: utf-8

from sqlalchemy import create_engine, text
from datetime import datetime
import openai
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import tiktoken
import time
import re
from dotenv import load_dotenv
import os

load_dotenv()

def fetch_data_for_specific_channels(engine, target_channels):
    """Fetch messages from the last 24 hours for specific channels."""
    print(f"Starting data fetch for specific channels at {datetime.now()}")
    
    target_channels_set = set(target_channels)
    
    main_query = text("""
        SELECT 
            pt.id AS message_id,
            pt.message,
            pt.date,
            pt.views,
            pt.forwards,
            c.title AS channel_title,
            c.username AS channel_username
        FROM post_texts pt
        JOIN channels c ON pt.peer_id = c.id
        WHERE pt.date >= NOW() - INTERVAL '24 hours'
          AND c.username = ANY(:channel_usernames)
        ORDER BY pt.date DESC
    """)
    
    try:
        with engine.connect() as conn:
            print("Fetching messages from the last 24 hours...")
            result = conn.execute(
                main_query, 
                {"channel_usernames": list(target_channels_set)}
            ).fetchall()
            
            messages = [{
                "message_id": row[0],
                "message": row[1],
                "date": row[2],
                "views": row[3],
                "forwards": row[4],
                "channel_title": row[5],
                "channel_username": row[6],
            } for row in result]
            
            print(f"Total messages fetched: {len(messages)}")
            return messages
            
    except Exception as e:
        print(f"Error during data fetch: {e}")
        return []


# Define the list of channels
channels_list = [
    'severnygorod', 'agapov_fi', 'karaulny', 'rusbrief', 'octgnews', 'tass_agency', 'baltnews',
    'fontankaspb', 'dprunews', 'sp_1703', 'glavmedia', 'houseofcardseurope', 'good78news',
    'rian_ru', 'belta_telegramm', 'radiogovoritmsk', 'bbbreaking', 'paperpaper_ru', 'nevnov',
    'swodki', 'vzglyad_ru', 'parstodayrussian', 'ukraina_ru', 'solovievlive', 'rossiyaneevropa',
    'online47news', 'riafan', 'radiomirby', 'dirtytatarstan', 'rgrunews', 'inosmichannel',
    'sputnikby', 'rbc_news', 'ssigny', 'boyart777', 'lentadnya', 'radiosvoboda', 'kommersant',
    'topspb_tv', 'allnews47', 'rt_russian', 'absatzmedia', 'match_tv', 'truekpru', 'bbcrussian',
    'houseofcardsrussia', 'OdessaRussi', 'Novoeizdanie', 'rus_demiurge', 'stranaua', 'rbc_brief',
    'aifonline', 'ostashkonews', 'dimsmirnov175', 'ateobreaking', 'infantmilitario', 'UAnotRU',
    'smotri_media', 'thehandofthekremlin', 'leningrad_guide', 'izvestia', 'meduzalive',
    'highlylikely20', 'rentv_news', 'znua_live', 'atn_btrc', 'vestiru24', 'chvkmedia',
    'espresotb', 'kshulika', 'orientsouthrus', 'dwglavnoe', 'ZOVcrimea', 'Belarus_VPO',
    'readovkanews', 'ranarod', 'gazetaru', 'nexta_live', 'ntvnews', 'uniannet', 'lady_north',
    'fuckyouthatswhy', 'nstarikovru', 'new_militarycolumnist', 'mk_ru', 'lab365', 'go338',
    'postovo', 'asphaltt', 'politkraina', 'rlz_the_kraken', 'ru2ch', 'bfmnews', 'russtrat',
    'tv360', 'radio_sputnik', 'minut30', 'pluanews', 'rtvinews', 'interfaxonline',
    'istorijaoruzijaz', 'currenttime', 'sputniklive', 'newsgrpua', 'srochnow', 'ukrpravda_news',
    'first_political', 'oldlentach', 'RUSanctions', 'Pravda_Gerashchenko', 'warhistoryalconafter',
    'ivan_utenkov13', 'TCH_channel', 'the_moscow_post', 'UkraineNow', 'openukraine',
    'ukr_shvydko', 'lentachold', 'huyovy_kharkiv', 'kontext_channel', 'russica2', 'tvrain',
    'operativnozsu', 'rus_now_news', 'voynareal', 'lachentyt', 'russianonwars',
    'dmytrogordon_official', 'banksta', 'TolkoPoDely', 'rybar', 'rhymestg', 'ragnarockkyiv',
    'ukraina24tv', 'bankrollo', 'truexanewsua', 'sheyhtamir1974', 'aleksandrsemchenko',
    'tsaplienko', 'varlamov_news', 'DavydovIn', 'boris_rozhin', 'RVvoenkor', 'redacted6',
    'zerkalo_io', 'voenacher', 'Mikle1On', 'UaOnlii', 'vchkogpu', 'kaktovottak', 'novosti_efir',
    'shot_shot', 'insiderUKR', 'slavaded1337', 'bloodysx', 'breakingmash', 'readovkaru',
    'ostorozhno_novosti', 'okoo_ukr', 'Cbpub', 'warfakes', 'montyan2', 'moscowmap',
    'asupersharij', 'nevzorovtv', 'V_Zelenskiy_official', 'yurasumy'
]
# # Pipeline to fetch, summarize, and post to Slack
# messages = fetch_data_for_specific_channels(engine, channels_list)

# Keywords for Finland-related content in English, Russian, and Ukrainian
keywords_regex = [
    r"\bFinland(?:ic|ian)?\b",
    r"\bFinn(?:ish)?\b",
    r"\bФинлянд(?:(?:ия|ии|ие|ию|ией|ий))?\b",
    r"\bфин(?:ский|ская|ское|ские|ского|скому|ским|ской|ских|скими)?\b",
    r"\bФінлянді(?:(?:я|ї|ю|єю|їй))?\b",
    r"\bфін(?:ський|ська|ське|ські|ського|ському|ським|ською|ських|ськими)?\b"
]

def filter_messages_with_regex(messages, regex_patterns=keywords_regex):
    """
    Filter messages based on a list of regex patterns.
    
    Args:
        messages (list): List of message dictionaries containing 'message' key.
        regex_patterns (list): List of regex patterns to match against messages.
        
    Returns:
        list: Filtered list of messages containing any of the patterns.
    """
    if not messages:
        return []
        
    filtered_messages = []
    compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in regex_patterns]
    
    for message in messages:
        # Skip if message is None or empty
        if not message.get('message'):
            continue
            
        # Check each pattern against the message
        for pattern in compiled_patterns:
            if pattern.search(message['message']):
                filtered_messages.append(message)
                break  # Stop checking other patterns once a match is found
                
    return filtered_messages

def summarize_with_openai(messages):
    """Create a summary of messages using OpenAI with specific focus on Finnish topics."""
    if not messages:
        return "No messages found for summarization."

    def create_telegram_link(channel_username, message_id):
        """Create a Telegram message link."""
        if not channel_username:
            return str(message_id)
        return f"<https://t.me/{channel_username}/{message_id}>"

    def count_tokens(text):
        """Count tokens for GPT-3.5-turbo model."""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(text))

    # Prepare messages text with IDs and links
    messages_text = "\n\n".join([
        f"Message ID: {msg['message_id']}\n"
        f"Channel: {msg['channel_title']} ({msg['channel_username']})\n"
        f"Date: {msg['date']}\n"
        f"Message: {msg['message'][:500]}\n"
        f"Views: {msg['views']}, Forwards: {msg['forwards']}\n"
        f"Link: {create_telegram_link(msg['channel_username'], msg['message_id'])}"
        for msg in messages[:20]
    ])

    system_message = {
        "role": "system", 
        "content": """You are an expert political analyst and journalist specializing in Finnish affairs capable of summarizing and finding commonalities in Russian-language messages about Finland or Finnish topics. Focus exclusively on newsworthy developments:
    - Major policy decisions and governmental actions
    - Economic and trade developments
    - Security and defense matters
    - Diplomatic relations
    - Infrastructure and strategic developments
    - Any other significant national developments
    
    Exclude:
    - Cultural events
    - Social media discussions
    - Entertainment news
    - Human interest stories
    - Anecdotal mentions
    - Humor or entertainment
    
    Writing requirements:
    1. Write in clear journalistic style
    2. Always cite message IDs in parentheses within sentences
    3. Focus on factual reporting
    4. If only no newsworthy content exists, state (without making any summary): "Nothing newsworthy was mentioned the last day"
    5. Maintain neutral, objective tone"""
    }
    
    user_message = {
        "role": "user",
        "content": f"""Analyze these Finland-related messages for newsworthy developments and produce a summary based on them:
    
    {messages_text}
    
    If newsworthy content exists, structure your response as follows:
    
    Overview:
    [Two newlines after title]
    Brief summary of key developments.
    
    Key Topics:
    [Two newlines after title]
    Detailed coverage of significant developments, with each development in its own paragraph.
    
    If no newsworthy content exists at all, simply state (without making any summary):
    "Nothing newsworthy was mentioned the last day"
    
    Requirements:
    1. Focus on verified developments
    2. Always cite message IDs in parentheses
    3. Maintain professional writing style and neutral tone while attributing claims to sources
    4. Group related developments together
    5. Only include significant developments
    6. Present information as channel claims using phrases like but not limited to:
       - "(message ID) reported that..."
       - "According to (message ID)..."
       - "Several channels (message IDs) claimed that..."
       """
    }

    # Rest of the function remains exactly the same (token counting, API call, etc.)

    # Count tokens and adjust if needed
    prompt_tokens = count_tokens(system_message["content"]) + count_tokens(user_message["content"])
    max_response_tokens = 1500
    total_tokens = prompt_tokens + max_response_tokens

    # Adjust prompt if it exceeds token limit
    if total_tokens > 4096:
        excess_tokens = total_tokens - 4096
        messages = messages[:max(1, 20 - excess_tokens // 200)]
        messages_text = "\n\n".join([
            f"Message ID: {msg['message_id']}\n"
            f"Channel: {msg['channel_title']} ({msg['channel_username']})\n"
            f"Date: {msg['date']}\n"
            f"Message: {msg['message'][:300]}\n"
            f"Views: {msg['views']}, Forwards: {msg['forwards']}\n"
            f"Link: {create_telegram_link(msg['channel_username'], msg['message_id'])}"
            for msg in messages
        ])
        user_message["content"] = user_message["content"].replace(
            user_message["content"].split("\n\n")[1], 
            messages_text
        )

    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[system_message, user_message],
                temperature=0.7,
                max_tokens=max_response_tokens,
                top_p=0.9,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                return "Error: Rate limit exceeded. Please try again later."
        except openai.error.APIError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return f"OpenAI API error: {str(e)}"
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    return "Failed to generate summary after multiple attempts."


#saved like this for alternative summarization method
def summarize_with_ollama(messages):
    """Create a summary of messages using a local Ollama model."""
    pass

# Set this variable to 1 for OpenAI or 2 for Ollama
SUMMARY_METHOD = 1
def summarize_with_ai(messages):
    """Main function to summarize messages based on selected method."""
    if SUMMARY_METHOD == 1:
        return summarize_with_openai(messages)
    else:
        return summarize_with_ollama(messages)

# Slack and OpenAI credentials
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
client = WebClient(token=SLACK_BOT_TOKEN)

def post_to_slack(messages, summary):
    """Post enhanced summary and analysis to Slack."""
    if not messages:
        return "No messages to post."

    def create_telegram_link(channel_username, message_id):
        """Create a Telegram message link with channel username as display text."""
        return f"https://t.me/{channel_username}/{message_id}"

    # Process the summary to create links
    modified_summary = summary
    
    # Create a mapping of message_ids to their channel usernames
    msg_map = {str(msg['message_id']): msg['channel_username'] for msg in messages}
    
    # First, handle the message IDs that appear in parentheses
    def replace_in_parentheses(match):
        content = match.group(1)  # Get content inside parentheses
        parts = [p.strip() for p in content.split(',')]
        
        processed_parts = []
        for part in parts:
            if part in msg_map:
                # If it's a message ID, create a link
                link = create_telegram_link(msg_map[part], part)
                processed_parts.append(f"<{link}|{msg_map[part]}>")
            else:
                # If it's not a message ID (e.g., channel name), keep as is
                processed_parts.append(part)
        
        return f"({', '.join(processed_parts)})"

    # Use regex to find and replace content within parentheses
    modified_summary = re.sub(r'\(([\d\w, ]+)\)', replace_in_parentheses, modified_summary)
        

    # Calculate date range from messages
    dates = [msg['date'] for msg in messages]
    date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}" if dates else "N/A"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def calculate_metrics(messages):
        """Calculate all metrics needed for the Slack message."""
        if not messages:
            return {
                'total_messages': 0,
                'total_views': 0,
                'total_forwards': 0,
                'avg_views': 0,
                'avg_forwards': 0,
                'engagement_rate': 0,
                'forwards_per_post_avg': 0,
                'views_to_forwards_ratio_avg': 0,
                'virality_score': 0,
                'unique_channels': 0,
                'posts_per_day': 0,
                'max_daily_posts': 0
            }
    
        # Basic metrics remain the same
        total_messages = len(messages)
        total_views = sum(msg['views'] or 0 for msg in messages)
        total_forwards = sum(msg['forwards'] or 0 for msg in messages)
        avg_views = total_views / total_messages if total_messages > 0 else 0
        avg_forwards = total_forwards / total_messages if total_messages > 0 else 0
        engagement_rate = (total_forwards / total_views * 100) if total_views > 0 else 0
        
        # New engagement metrics remain the same
        forwards_per_post_avg = total_forwards / total_messages if total_messages > 0 else 0
        views_to_forwards_ratio_avg = (total_views / total_forwards) if total_forwards > 0 else 0
        virality_score = (forwards_per_post_avg / views_to_forwards_ratio_avg * 100) if views_to_forwards_ratio_avg > 0 else 0
    
        # Distribution metrics with corrected date handling
        days_count = {}
        for msg in messages:
            # Use the date directly since it's already a DATE type
            date = msg['date']
            days_count[date] = days_count.get(date, 0) + 1
        
        posts_per_day = total_messages / len(days_count) if days_count else 0
        max_daily_posts = max(days_count.values()) if days_count else 0
        unique_channels = len(set(msg['channel_username'] for msg in messages))
        # total_potential_audience = sum(channel['participantscount'] for channel in channels) # must be fetched from db first 
        # audience_reach_rate = (total_views / total_potential_audience * 100) if total_potential_audience > 0 else 0
        
        return {
            'total_messages': total_messages,
            'total_views': total_views,
            'total_forwards': total_forwards,
            'avg_views': avg_views,
            'avg_forwards': avg_forwards,
            'engagement_rate': engagement_rate,
            'forwards_per_post_avg': forwards_per_post_avg,
            'views_to_forwards_ratio_avg': views_to_forwards_ratio_avg,
            'virality_score': virality_score,
            'unique_channels': unique_channels,
            'posts_per_day': posts_per_day,
            'max_daily_posts': max_daily_posts,
            # 'audience_reach_rate': audience_reach_rate
        }
    
    # Then before creating blocks:
    metrics = calculate_metrics(messages)

    blocks = blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🇫🇮 Finland-Related Messages Summary"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Analysis Period:* {date_range} | 🕒 Generated: {current_time}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔍 Analysis of Messages about Finland and Generated Summary:*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": modified_summary
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*📊 Basic Metrics*\n"
                    f"• Total Messages Analyzed (related to Finland): {metrics['total_messages']}\n"
                    f"• Total Views: {metrics['total_views']:,}\n"
                    f"• Total Forwards: {metrics['total_forwards']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📈 Average Metrics*\n"
                    f"• Avg Views/Post: {metrics['avg_views']:.1f} \n_(how many views each post related to Finland gets on average)_\n"
                    f"• Avg Forwards/Post: {metrics['avg_forwards']:.1f} \n_(how many times each post related to Finland is shared on average)_\n"
                    f"• Base Engagement: {metrics['engagement_rate']:.1f}% \n_(how many viewers share the content about Finland)_"
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*🔄 Advanced Engagement*\n"
                    f"• Views/Forwards Ratio: {metrics['views_to_forwards_ratio_avg']:.1f} \n_(how many people view before someone shares)_\n"
                    f"• Virality Score: {metrics['virality_score']:.1f}% \n_(how likely content is to spread: forwards/post ÷ views/forwards×100)_\n"
                    f"• Unique Channels: {metrics['unique_channels']} \n_(number of different channels posting about Finland)_"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📊 Distribution Patterns*\n"
                    f"• Posts/Day: {metrics['posts_per_day']:.1f} \n_(average number of posts each day)_\n"
                    f"• Peak Daily Posts: {metrics['max_daily_posts']} \n_(highest number of posts in one day)_\n"
                    f"• Channel Activity Ratio: {(metrics['total_messages'] / metrics['unique_channels']):.1f} \n_(average posts about Finland per channel)_"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 _Message IDs are clickable links to original posts_"
                }
            ]
        }
    ]

    try:
        client.chat_postMessage(
            channel=CHANNEL_ID, 
            blocks=blocks, 
            text=f"Finland News Intelligence Report ({current_time})",
            unfurl_links=True,
            unfurl_media=True
        )
        print("Enhanced report posted successfully to Slack.")
    except SlackApiError as e:
        print(f"Slack API error: {e}")

# post_to_slack(messages, summary)

def translate_summary_to_finnish(summary):
    """
    Translate the generated summary to Finnish using OpenAI's model.
    
    Args:
        summary (str): The English summary text to translate
        
    Returns:
        str: Finnish translation of the summary or error message
    """
    if not summary:
        return "Ei yhteenvetoa käännettäväksi."
    
    try:
        system_message = {
            "role": "system",
            "content": "You are a professional translator specializing in English to Finnish translation. Translate the text while preserving all formatting, numbers, and special characters. Keep message IDs in their original form."
        }
        
        user_message = {
            "role": "user",
            "content": f"Translate the following text to Finnish:\n\n{summary}"
        }
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
            temperature=0.5,
            max_tokens=1500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Käännösvirhe: {str(e)}"

def post_finnish_to_slack(messages, summary):
    """Post enhanced summary and analysis to Slack."""
    if not messages:
        return "No messages to post."

    def create_telegram_link(channel_username, message_id):
        """Create a Telegram message link with channel username as display text."""
        return f"https://t.me/{channel_username}/{message_id}"

    # Process the summary to create links
    modified_summary = summary
    
    # Create a mapping of message_ids to their channel usernames
    msg_map = {str(msg['message_id']): msg['channel_username'] for msg in messages}
    
    # First, handle the message IDs that appear in parentheses
    def replace_in_parentheses(match):
        content = match.group(1)  # Get content inside parentheses
        parts = [p.strip() for p in content.split(',')]
        
        processed_parts = []
        for part in parts:
            if part in msg_map:
                # If it's a message ID, create a link
                link = create_telegram_link(msg_map[part], part)
                processed_parts.append(f"<{link}|{msg_map[part]}>")
            else:
                # If it's not a message ID (e.g., channel name), keep as is
                processed_parts.append(part)
        
        return f"({', '.join(processed_parts)})"

    # Use regex to find and replace content within parentheses
    modified_summary = re.sub(r'\(([\d\w, ]+)\)', replace_in_parentheses, modified_summary)

    # Calculate date range from messages
    dates = [msg['date'] for msg in messages]
    date_range = f"{min(dates).strftime('%Y-%m-%d')} to {max(dates).strftime('%Y-%m-%d')}" if dates else "N/A"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def calculate_metrics(messages):
        """Calculate all metrics needed for the Slack message."""
        if not messages:
            return {
                'total_messages': 0,
                'total_views': 0,
                'total_forwards': 0,
                'avg_views': 0,
                'avg_forwards': 0,
                'engagement_rate': 0,
                'forwards_per_post_avg': 0,
                'views_to_forwards_ratio_avg': 0,
                'virality_score': 0,
                'unique_channels': 0,
                'posts_per_day': 0,
                'max_daily_posts': 0
            }
    
        # Basic metrics remain the same
        total_messages = len(messages)
        total_views = sum(msg['views'] or 0 for msg in messages)
        total_forwards = sum(msg['forwards'] or 0 for msg in messages)
        avg_views = total_views / total_messages if total_messages > 0 else 0
        avg_forwards = total_forwards / total_messages if total_messages > 0 else 0
        engagement_rate = (total_forwards / total_views * 100) if total_views > 0 else 0
        
        # New engagement metrics remain the same
        forwards_per_post_avg = total_forwards / total_messages if total_messages > 0 else 0
        views_to_forwards_ratio_avg = (total_views / total_forwards) if total_forwards > 0 else 0
        virality_score = (forwards_per_post_avg / views_to_forwards_ratio_avg * 100) if views_to_forwards_ratio_avg > 0 else 0
    
        # Distribution metrics with corrected date handling
        days_count = {}
        for msg in messages:
            # Use the date directly since it's already a DATE type
            date = msg['date']
            days_count[date] = days_count.get(date, 0) + 1
        
        posts_per_day = total_messages / len(days_count) if days_count else 0
        max_daily_posts = max(days_count.values()) if days_count else 0
        unique_channels = len(set(msg['channel_username'] for msg in messages))
        # total_potential_audience = sum(channel['participantscount'] for channel in channels) # must be fetched from db first 
        # audience_reach_rate = (total_views / total_potential_audience * 100) if total_potential_audience > 0 else 0
        
        return {
            'total_messages': total_messages,
            'total_views': total_views,
            'total_forwards': total_forwards,
            'avg_views': avg_views,
            'avg_forwards': avg_forwards,
            'engagement_rate': engagement_rate,
            'forwards_per_post_avg': forwards_per_post_avg,
            'views_to_forwards_ratio_avg': views_to_forwards_ratio_avg,
            'virality_score': virality_score,
            'unique_channels': unique_channels,
            'posts_per_day': posts_per_day,
            'max_daily_posts': max_daily_posts,
            # 'audience_reach_rate': audience_reach_rate
        }
    
    # Then before creating blocks:
    metrics = calculate_metrics(messages)

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🇫🇮 Suomeen liittyvien viestien yhteenveto"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"*Analyysiajanjakso:* {date_range} | 🕒 Luotu: {current_time}"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*🔍 Suomea koskevien viestien analyysi ja yhteenveto:*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": modified_summary
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*📊 Perustiedot*\n"
                    f"• Analysoituja viestejä (Suomeen liittyvät): {metrics['total_messages']}\n"
                    f"• Näyttökerrat yhteensä: {metrics['total_views']:,}\n"
                    f"• Edelleenlähetykset yhteensä: {metrics['total_forwards']:,}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📈 Keskiarvot*\n"
                    f"• Näyttöjä/viesti: {metrics['avg_views']:.1f} \n_(kuinka monta näyttökertaa kukin Suomeen liittyvä viesti saa keskimäärin)_\n"
                    f"• Edelleenlähetyksiä/viesti: {metrics['avg_forwards']:.1f} \n_(kuinka monta kertaa kutakin Suomeen liittyvää viestiä jaetaan keskimäärin)_\n"
                    f"• Perussitouttavuus: {metrics['engagement_rate']:.1f}% \n_(kuinka moni katsojista jakaa Suomeen liittyvää sisältöä)_"
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*🔄 Edistyneet sitoutumistiedot*\n"
                    f"• Näyttöjen/edelleenlähetysten suhde: {metrics['views_to_forwards_ratio_avg']:.1f} \n_(kuinka moni katsoo ennen kuin joku jakaa)_\n"
                    f"• Viraalisuuspisteet: {metrics['virality_score']:.1f}% \n_(sisällön leviämistodennäköisyys: edelleenlähetykset/viesti ÷ näytöt/edelleenlähetykset×100)_\n"
                    f"• Eri kanavat: {metrics['unique_channels']} \n_(Suomesta julkaisevien kanavien määrä)_"
                },
                {
                    "type": "mrkdwn",
                    "text": "*📊 Jakaumamallit*\n"
                    f"• Viestejä/päivä: {metrics['posts_per_day']:.1f} \n_(viestien keskimäärä päivässä)_\n"
                    f"• Päivän huippumäärä: {metrics['max_daily_posts']} \n_(suurin viestimäärä yhtenä päivänä)_\n"
                    f"• Kanava-aktiivisuussuhde: {(metrics['total_messages'] / metrics['unique_channels']):.1f} \n_(Suomea koskevien viestien keskiarvo per kanava)_"
                }
            ]
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 _Viesti-ID:t ovat klikattavia linkkejä alkuperäisiin julkaisuihin_"
                }
            ]
        }
    ]

    try:
        client.chat_postMessage(
            channel=CHANNEL_ID, 
            blocks=blocks, 
            text=f"Suomeen Liittyvien Viestien Yhteenveto (sama kuin edellinen suomeksi) ({current_time})",
            unfurl_links=True,
            unfurl_media=True
        )
        print("Enhanced report posted successfully to Slack.")
    except SlackApiError as e:
        print(f"Slack API error: {e}")

def post_no_messages_notification():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    today = datetime.now().strftime("%Y-%m-%d")
    
    english_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Today ({today}) no messages about Finland 🇫🇮 found in the selected channels!*"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Generated: {current_time}"
                }
            ]
        }
    ]
    
    finnish_blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Tänään ({today}) valituista kanavista ei löytynyt Suomeen 🇫🇮 liittyviä viestejä!*"
            }
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Luotu: {current_time}"
                }
            ]
        }
    ]
    
    try:
        client.chat_postMessage(
            channel=CHANNEL_ID,
            blocks=english_blocks,
            text=f"No messages about Finland found {today}",
            unfurl_links=False
        )
        
        client.chat_postMessage(
            channel=CHANNEL_ID,
            blocks=finnish_blocks,
            text=f"Ei Suomeen liittyviä viestejä {today}",
            unfurl_links=False
        )
        print("No message alert posted successfully to Slack.")
    except SlackApiError as e:
        print(f"Error posting to Slack: {e}")

def main():
    # Replace with your PostgreSQL credentials
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    
    # Create a connection string
    connection_string = f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}'
    openai.api_key = os.getenv('OPENAI_API_KEY')
    # Create a SQLAlchemy engine
    engine = create_engine(connection_string)

    # Test database connection
    try:
        with engine.connect() as conn:
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
    
    # Process messages
    messages = fetch_data_for_specific_channels(engine, channels_list)
    filtered_messages = filter_messages_with_regex(messages, keywords_regex)
    if filtered_messages:
        summary = summarize_with_ai(filtered_messages)
        post_to_slack(filtered_messages, summary)
        finnish_summary = translate_summary_to_finnish(summary)
        post_finnish_to_slack(filtered_messages, finnish_summary)
    else:
        post_no_messages_notification()

if __name__ == '__main__':
    main()