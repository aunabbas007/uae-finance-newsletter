import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import feedparser
import openai

def fetch_uae_news():
    """Fetches recent UAE finance, tax, and audit news from Google News RSS."""
    print("Fetching news from Google News RSS...")
    # Search query targeting UAE and finance/tax/audit topics in the last 24 hours
    query = "UAE+finance+OR+tax+OR+audit+when:1d"
    url = f"https://news.google.com/rss/search?q={query}"
    
    feed = feedparser.parse(url)
    
    articles = []
    # Limit to top 30 articles to avoid sending too much context to the LLM
    for entry in feed.entries[:30]:
        title = entry.title
        link = entry.link
        published = entry.published if 'published' in entry else 'Recent'
        articles.append(f"- {title} ({published})\n  Link: {link}")
        
    return "\n\n".join(articles)

def summarize_news(news_text):
    """Uses Groq to summarize the news text into a 3-point newsletter."""
    print("Summarizing news with Groq...")
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    client = openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    
    prompt = f"""
    You are an expert financial analyst and newsletter editor specializing in the UAE region.
    I will provide you with a list of recent news article titles and links related to UAE finance, tax, and audit.
    
    Your task is to summarize this information into a professional, engaging 3-point newsletter.
    
    Rules:
    1. Extract the 3 most important and impactful themes or stories from the provided news.
    2. Write a concise, professional paragraph for each point.
    3. Include 1-2 relevant source links at the end of each point (use markdown format `[Source](url)`).
    4. Provide the output in clean HTML format suitable for an email body (do not include ```html blocks, just the HTML tags).
    5. Start with a brief, professional greeting.
    6. Ensure the tone is objective and informative.
    
    Here is the news data:
    {news_text}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def send_email(html_content):
    """Sends the summarized newsletter via Gmail SMTP."""
    print("Sending email...")
    sender_email = os.environ.get("GMAIL_USER")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("EMAIL_RECEIVER", "mhmdhfizabbas@gmail.com")
    
    if not sender_email or not sender_password:
        print("WARNING: GMAIL_USER or GMAIL_APP_PASSWORD environment variables not set. Email will not be sent.")
        print("Generated Newsletter Content:\n")
        print(html_content)
        return

    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Daily UAE Finance & Tax Update"
    msg['From'] = f"UAE Finance Bot <{sender_email}>"
    msg['To'] = receiver_email

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent successfully to {receiver_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    try:
        news_data = fetch_uae_news()
        if not news_data:
            print("No news found for the last 24 hours.")
        else:
            summary_html = summarize_news(news_data)
            send_email(summary_html)
    except Exception as e:
        print(f"An error occurred: {e}")
