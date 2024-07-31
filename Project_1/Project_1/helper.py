import pandas
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
from django.conf import settings
import re
import matplotlib.pyplot as plt
from textblob import TextBlob

# Set the font to a suitable emoji-supporting font
plt.rcParams['font.family'] = 'Noto Color Emoji'

# Your code to create and display the graph


settings.configure(
    DEBUG=True,

)


extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links)
def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x,df

def create_wordcloud(selected_user,df):

    # f = open('stop_words.txt', 'r')
    # stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    # def remove_stop_words(message):
    #     y = []
    #     for word in message.lower().split():
    #         if word not in stop_words:
    #             y.append(word)
    #     return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    # temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):

    f = open('stop_words.txt','r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

# def emoji_helper(selected_user, df):
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     emojis = []
#
#     for message in df['message']:
#         # Replace emojis with their text representations
#         text_message = emoji.demojize(message)
#         # Find text representations of emojis
#         emoji_list = [word for word in text_message.split() if word.startswith(':') and word.endswith(':')]
#         emojis.extend(emoji_list)
#
#     emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
#     return emoji_df
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []

    for message in df['message']:
        # Use a regular expression to find emojis in the message
        emoji_list = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U0001FB00-\U0001FBFF]', message)
        emojis.extend(emoji_list)

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df
def analyze_sentiment(message):
    analysis = TextBlob(message)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"
# def monthly_timeline(selected_user,df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
#
#     time = []
#     for i in range(timeline.shape[0]):
#         time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
#
#     timeline['time'] = time
#
#     return timeline
#
# def daily_timeline(selected_user,df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     daily_timeline = df.groupby('only_date').count()['message'].reset_index()
#
#     return daily_timeline
#
# def week_activity_map(selected_user,df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     return df['day_name'].value_counts()
#
# def month_activity_map(selected_user,df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     return df['month'].value_counts()
#
# def activity_heatmap(selected_user,df):
#
#     if selected_user != 'Overall':
#         df = df[df['user'] == selected_user]
#
#     user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
#
#     return user_heatmap
#
