# UAE Finance Newsletter Automator

A Python automation project specification for collecting selected UAE finance and tax authority news feeds, generating a digest with Google's Gemini API, and sending the result by email.

## Documented sources
- UAE Federal Tax Authority RSS: https://tax.gov.ae/en/rss/rss.aspx
- UAE Ministry of Finance RSS: https://www.mof.gov.ae/en/media/news/pages/rss.aspx

## Technology
- Python 3.10+
- Google Gemini API (`google-generativeai`)
- `feedparser`
- `smtplib`
- GitHub Actions for scheduled automation

## Configuration
The project specification expects these values to be supplied through environment variables:
- `GEMINI_API_KEY`
- `GMAIL_USER`
- `GMAIL_PASS`

Use a Gmail App Password where required. Store credentials as GitHub Actions secrets or local environment variables. Never commit real keys or passwords.

## Expected behavior
If no relevant news is found for the day, the script should log `No News` and exit without sending an email.

## Run locally
Install the dependencies listed in `requirements.txt`, configure the environment variables, and run the repository's Python entry point.

Check the source files for the exact entry-point filename and workflow schedule.

## Author
[Aun Abbas](https://github.com/aunabbas007)
