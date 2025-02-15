import random
import textstat
import requests
from discord_webhook import DiscordWebhook
from bs4 import BeautifulSoup
import schedule
import time

# Discord WebHook URL (replace with your actual WebHook)
DISCORD_WEBHOOK_URL = "your_discord_webhook_url_here"

# Maximum syllable limit for headlines
MAX_SYLLABLE_LIMIT = 20

# Define the times you want to post (24-hour format)
POST_TIMES = ["09:00", "18:00"]  # Example: 9:00 AM and 6:00 PM

def get_news_from_website():
    """Fetches news headlines from a website (example: BBC)."""
    try:
        url = "https://www.bbc.com"  # Use the website of your choice
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scraping headlines (Example for BBC, updating for more general approach)
        headlines = [headline.get_text() for headline in soup.find_all(['h1', 'h2', 'h3'])]  # Look for multiple possible tags

        # Filter out headlines that exceed the syllable limit
        headlines = [h for h in headlines if count_syllables(h) <= MAX_SYLLABLE_LIMIT]

        if not headlines:
            print("No suitable headlines found.")
        return headlines[:50]  # Adjust number of headlines if needed
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def count_syllables(text):
    """Counts syllables in a given text using textstat."""
    return textstat.syllable_count(text)

def create_haiku(headlines):
    """Creates a haiku (5-7-5) from news headlines, allowing slight variations."""
    
    # Allowing more flexibility in syllable count for 5 and 7-syllable lines
    five_syllable = [h for h in headlines if 4 <= count_syllables(h) <= 6]
    seven_syllable = [h for h in headlines if 6 <= count_syllables(h) <= 8]

    if len(five_syllable) >= 2 and len(seven_syllable) >= 1:
        haiku = f"{random.choice(five_syllable)}\n{random.choice(seven_syllable)}\n{random.choice(five_syllable)}"
        return haiku
    return "Couldn't form a haiku!"

def send_to_discord(haiku):
    """Sends the haiku to a Discord channel via WebHook."""
    try:
        webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=f"**Today's Haiku:**\n\n{haiku}")
        webhook.execute()
        print("Haiku posted to Discord!")
    except Exception as e:
        print(f"Error sending message to Discord: {e}")

def job():
    """Function to get news, generate haiku, and send to Discord."""
    headlines = get_news_from_website()
    
    if not headlines:
        print("No headlines found. Exiting.")
        return

    haiku = create_haiku(headlines)
    print(f"Generated Haiku:\n{haiku}")
    
    send_to_discord(haiku)

def schedule_jobs():
    """Schedule the job to post at specific times."""
    for post_time in POST_TIMES:
        schedule.every().day.at(post_time).do(job)
        print(f"Scheduled a post at {post_time}")

def main():
    """Main function to schedule and run jobs."""
    schedule_jobs()
    
    while True:
        # Run the scheduled jobs
        schedule.run_pending()
        time.sleep(1)  # Wait for the next scheduled time

if __name__ == "__main__":
    main()
