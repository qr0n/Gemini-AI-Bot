from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Initialize Vader Sentiment Analyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
  """
  Analyzes the sentiment of a text string.

  Args:
      text: The text string to analyze.

  Returns:
      A dictionary containing the sentiment scores for positive, negative, neutral, and compound.
  """
  scores = analyzer.polarity_scores(text)
  return scores

while True:
    text = input()
    sentiment = get_sentiment(text)
    
    if sentiment['compound'] > 0.05:
      print("Positive sentiment!")
    elif sentiment['compound'] < -0.05:
      print("Negative sentiment.")
    else:
      print("Neutral sentiment.")

    print(sentiment)