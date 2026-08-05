import os
import sys
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
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    
    # Use a browser-like User-Agent to avoid being blocked by Google News
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    feed = feedparser.parse(url, agent=user_agent)
    
    # Check for HTTP status codes indicating failure (e.g. 403 Forbidden, 429 Too Many Requests)
    if hasattr(feed, 'status') and feed.status >= 400:
        raise RuntimeError(f"Google News RSS returned status code {feed.status}")
        
    # Check for parsing errors if no entries could be recovered
    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Failed to parse RSS feed: {feed.get('bozo_exception', 'Unknown parse error')}")
        
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
    
    Your task is to summarize this information into a professional newsletter.
    
    Rules:
    1. Start the email EXACTLY with: "Dear Hafiz Abbas," followed by two blank lines.
    2. Extract the 3 most important and impactful themes or stories from the provided news.
    3. For each of the 3 stories, format it exactly like a professional LinkedIn post:
       - Provide a short, engaging 1-2 sentence introductory paragraph explaining the news.
       - Add a blank line, then write "This gives companies an opportunity to:" (or something similar depending on the context).
       - Add a blank line, then provide 3-4 bullet points extracting the key details. Start each bullet point on a NEW LINE with the '✅' emoji.
       - Add a blank line, then provide a short concluding sentence.
       - Add a blank line, then add relevant hashtags (e.g., #UAE #Finance #Tax).
       - Add a blank line, then include the source link.
       - Add a clear separator (like "----------------------------------------") before the next story.
    4. Provide the output in plain text. DO NOT use any HTML tags. Use standard newlines to create spacing.
    5. Ensure the tone is objective, professional, and informative.
    
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
    
    raw_content = response.choices[0].message.content
    
    # Convert plain text newlines to HTML line breaks so it renders correctly in the email client
    html_formatted = raw_content.replace('\n', '<br>')
    
    # Wrap in a clean, professional font style
    final_html = f"<div style='font-family: Arial, sans-serif; font-size: 15px; line-height: 1.6; color: #1a1a1a; max-width: 800px; margin: 0 auto;'>{html_formatted}</div>"
    
    return final_html

def send_email(html_content):
    """Sends the summarized newsletter via Gmail SMTP."""
    print("Sending email...")
    sender_email = os.environ.get("GMAIL_USER")
    sender_password = os.environ.get("GMAIL_APP_PASSWORD")
    receiver_email = os.environ.get("EMAIL_RECEIVER", "mhmdhfizabbas@gmail.com")
    
    if not sender_email or not sender_password:
        raise ValueError("GMAIL_USER or GMAIL_APP_PASSWORD environment variables are not set.")

    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Daily UAE Finance & Tax Update"
    msg['From'] = f"UAE Finance Bot <{sender_email}>"
    msg['To'] = receiver_email

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print(f"Email sent successfully to {receiver_email}!")

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
        sys.exit(1)
