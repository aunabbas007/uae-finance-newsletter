# UAE Finance Automator Specs

## Tech Stack
- Language: Python 3.10+
- AI: Google Gemini API (google-generativeai)
- Logic: feedparser, smtplib
- Automation: GitHub Actions (Standard Ubuntu Runner)

## Sources
- FTA News: https://tax.gov.ae/en/rss/rss.aspx
- MoF News: https://www.mof.gov.ae/en/media/news/pages/rss.aspx

## Requirements
- The email must be sent from a Gmail account using an 'App Password'.
- All sensitive keys (GEMINI_API_KEY, GMAIL_USER, GMAIL_PASS) must be pulled from os.environ.
- If no news is found for the day, the script should log "No News" and exit without sending an email.