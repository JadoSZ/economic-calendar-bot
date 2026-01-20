import requests
from datetime import datetime, timedelta
import os

WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

def send_test_message():
    """Send a test message to verify the bot works"""
    embed = {
        "title": "🎉 Economic Calendar Bot is Live!",
        "description": "Your bot is successfully configured and ready to send alerts.",
        "color": 5763719,
        "fields": [
            {
                "name": "📅 Weekly Preview",
                "value": "Every Monday at 8 AM UTC",
                "inline": False
            },
            {
                "name": "⏰ D-1 Reminders",
                "value": "Daily at 8 AM UTC for next day's events",
                "inline": False
            },
            {
                "name": "📊 Results",
                "value": "Posted as data is released",
                "inline": False
            }
        ],
        "footer": {
            "text": "Economic Calendar Bot • Ready to track medium & high impact U.S. events"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    data = {
        "content": "✅ **Setup Complete!** Your economic calendar alerts are now active.",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("✅ Test message sent successfully!")
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_test_message()
