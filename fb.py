import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIG ===
ACCESS_TOKEN = "Yhttps://graph.facebook.com/v18.0/oauth/access_token?%20grant_type=fb_exchange_token&%20client_id=1023167986411330&%20client_secret=eb12d45b5d866b6518e87df43b96f1bd&%20fb_exchange_token=EAAOikNxgJ0IBO3mk94mMCsdDjpuCBjWFZCknTCjSjvtJQwpJu57chJCwrhtEORiw97ZA8dyk7MdbZAijXryFDQtMEmoOcpedZBHbbZByjio5b0XgUgaI1Ly3bfUuU23Nhp18qUHKtro8gZCvq3zBq0ZCMLVAcK7tBCi4JBteaR9Nh55sIak3LyUSA2SGJHrvunLRFZATjZBovQ5c6sAZCvm9Pox5kjAPeEQ4hFZCRud98SGNRwM"
PAGES = ["tv3ghana", "PulseGhana", "dailygraphicghana", "TheGhanaWeb"]
VIRAL_LIKE_THRESHOLD = 1000
EMAIL_TO = "contact@omgvoice.com"
EMAIL_FROM = "your.email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # For Gmail, generate an App Password

# === FUNCTIONS ===
def get_page_id(page_name):
    url = f"https://graph.facebook.com/v18.0/{page_name}?access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("id")

def get_recent_posts(page_id):
    url = f"https://graph.facebook.com/v18.0/{page_id}/posts?fields=message,permalink_url,created_time,insights.metric(post_reactions_by_type_total)&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def is_viral(post):
    insights = post.get("insights", {}).get("data", [])
    for metric in insights:
        if metric.get("name") == "post_reactions_by_type_total":
            total_likes = sum(metric.get("values", [{}])[0].get("value", {}).values())
            return total_likes >= VIRAL_LIKE_THRESHOLD
    return False

def collect_viral_posts():
    viral_posts = []
    for page in PAGES:
        try:
            page_id = get_page_id(page)
            posts = get_recent_posts(page_id)
            for post in posts:
                if is_viral(post):
                    viral_posts.append({
                        "page": page,
                        "url": post.get("permalink_url"),
                        "text": post.get("message", "[No text]"),
                        "created": post.get("created_time")
                    })
        except Exception as e:
            print(f"Error processing {page}: {e}")
    return viral_posts

def send_email(viral_posts):
    subject = "🔥 Viral Ghana Facebook Posts"
    body = ""
    for post in viral_posts:
        body += f"Page: {post['page']}\n"
        body += f"Posted: {post['created']}\n"
        body += f"Text: {post['text'][:200]}...\n"
        body += f"URL: {post['url']}\n"
        body += "\n----------------------\n\n"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("✅ Email sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    posts = collect_viral_posts()
    if posts:
        send_email(posts)
    else:
        print("No viral posts found today.")
