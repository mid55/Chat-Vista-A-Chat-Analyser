import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
from textblob import TextBlob

Image.MAX_IMAGE_PIXELS = None
import seaborn as sns

plt.rcParams['font.family'] = 'Segoe UI Emoji'
st.set_page_config(page_title="Your App", page_icon="✅", layout="wide")

st.sidebar.title("CHAT VISTA")
st.sidebar.write("A Chat Analyser")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)
    st.dataframe(df)
    # fetch unique users

    user_list = df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)
    if st.sidebar.button("Show Analysis"):
        # Stats Area
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # daily timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # activity map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values, color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)
            # WordCloud
            st.title("Wordcloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # most common words
            most_common_df = helper.most_common_words(selected_user, df)

            fig, ax = plt.subplots()

            ax.barh(most_common_df[0], most_common_df[1])
            plt.xticks(rotation='vertical')

            st.title('Most commmon words')
            st.pyplot(fig)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)
        st.title("Emoji Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)
        with col2:
            fig, ax = plt.subplots()
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
            st.pyplot(fig)

        # sentiment analysis
        df['sentiment'] = df['message'].apply(helper.analyze_sentiment)
        st.title("Sentiment Analysis Graph")
        sentiment_counts = df['sentiment'].value_counts()
        st.bar_chart(sentiment_counts)
        #
        # # Sentiment Analysis
        # st.title("Sentiment Analysis")
        # selected_messages = df[df['user'] == selected_user]['message']
        #
        # positives, negatives, neutrals = 0, 0, 0
        #
        # for message in selected_messages:
        #     analysis = TextBlob(message)
        #     polarity = analysis.sentiment.polarity
        #     subjectivity = analysis.sentiment.subjectivity
        #
        #     if polarity > 0:
        #         sentiment = "Positive"
        #         positives += 1
        #     elif polarity < 0:
        #         sentiment = "Negative"
        #         negatives += 1
        #     else:
        #         sentiment = "Neutral"
        #         neutrals += 1
        #
        #     st.write(f"Message: {message}")
        #     st.write(f"Sentiment: {sentiment}")
        #     st.write(f"Polarity: {polarity}")
        #     st.write(f"Subjectivity: {subjectivity}")
        #     st.write("------")
        #
        # st.title("Sentiment Summary")
        # st.write(f"Total Messages: {len(selected_messages)}")
        # st.write(f"Positives: {positives}")
        # st.write(f"Negatives: {negatives}")
        # st.write(f"Neutrals: {neutrals}")

        st.title("Sentiment Analysis")


        def analyze_sentiment(message):
            analysis = TextBlob(message)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity

            if polarity > 0:
                sentiment = "Positive"
            elif polarity < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            return sentiment, polarity, subjectivity


        if selected_user == 'Overall':
            selected_messages = df['message']
        else:
            selected_messages = df[df['user'] == selected_user]['message']

        sentiment_data = []

        for message in selected_messages:
            sentiment, polarity, subjectivity = analyze_sentiment(message)
            sentiment_data.append((message, sentiment, polarity, subjectivity))

        sentiment_df = pd.DataFrame(sentiment_data, columns=["Message", "Sentiment", "Polarity", "Subjectivity"])

        st.dataframe(sentiment_df)

        st.title("Sentiment Summary")

        if selected_user == 'Overall':
            st.write(f"Total Messages: {len(selected_messages)}")
        else:
            st.write(f"Total Messages for {selected_user}: {len(selected_messages)}")

        positives = sentiment_df[sentiment_df["Sentiment"] == "Positive"].shape[0]
        negatives = sentiment_df[sentiment_df["Sentiment"] == "Negative"].shape[0]
        neutrals = sentiment_df[sentiment_df["Sentiment"] == "Neutral"].shape[0]

        st.write(f"Positives: {positives}")
        st.write(f"Negatives: {negatives}")
        st.write(f"Neutrals: {neutrals}")




