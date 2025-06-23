from flask import Flask, request, render_template
import praw
import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import unicodedata
import re


load_dotenv()  # Loads .env variables

app = Flask(__name__)

reddit = praw.Reddit(
    client_id='fQVTvOimcw4u8j2wUIesqw',
    client_secret='RGutOhzGgeFXrUVmKVxeC3LLIn97RA',
    user_agent="stock-finder-webapp"

)

def summarize_text(text, max_length=200):
    # Clean up newlines & excessive spaces
    clean = ' '.join(text.split())
    # Truncate without cutting words abruptly
    if len(clean) > max_length:
        return clean[:max_length].rsplit(' ', 1)[0] + '...'
    return clean




# Create analyzer once
analyzer = SentimentIntensityAnalyzer()

def predict_sentiment(text):
    score = analyzer.polarity_scores(text)
    compound = score['compound']
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    num_Positive = 0
    num_Negative = 0
    num_Neutral= 0
    total_posts = 0

    if request.method == "POST":
        tickers = [ticker.strip().upper() for ticker in request.form["tickers"].split(",")]
        
        subreddit_names = ["wallstreetbets", "stocks", "investing"]  # add more as you want
        for name in subreddit_names:
            subreddit = reddit.subreddit(name)
            for submission in subreddit.new(limit=200):
                title = submission.title.upper()
                if any(ticker in title for ticker in tickers):
                    
                    summary = summarize_text(submission.selftext)



                    combined_text = f"{submission.title}\n{submission.selftext}"
                    sentiment = predict_sentiment(combined_text)

                    total_posts += 1

                    if sentiment == "Positive":
                        num_Positive += 1
                    if sentiment == "Negative":
                        num_Negative += 1
                    if sentiment == "Neutral":
                        num_Neutral += 1

                    results.append({
                        "title": submission.title,
                        "url": submission.url,
                        "body": summary,
                        "sentiment": sentiment 
                    })
    return render_template(
    "index.html",
    results=results,
    num_Positive=num_Positive,
    num_Negative=num_Negative,
    num_Neutral=num_Neutral,
    total_posts=total_posts
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
