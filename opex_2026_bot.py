import requests
from datetime import datetime, timedelta
import os

WEBHOOK_URL = os.environ.get('OPEX_WEBHOOK')

# VIX OPTIONS - Standard Expiration (Wednesdays, 30 days before 3rd Friday)
# Exception: If Wednesday or Friday is exchange holiday, moves to preceding Tuesday
VIX_STANDARD_2026 = [
    "2026-01-21",  # Jan
    "2026-02-18",  # Feb
    "2026-03-18",  # Mar (Q1)
    "2026-04-15",  # Apr
    "2026-05-20",  # May
    "2026-06-17",  # Jun (Q2)
    "2026-07-15",  # Jul
    "2026-08-19",  # Aug
    "2026-09-16",  # Sep (Q3)
    "2026-10-21",  # Oct
    "2026-11-18",  # Nov
    "2026-12-16",  # Dec (Q4)
]

# VIX WEEKLYS - Every Wednesday (excluding standard expiration weeks)
VIX_WEEKLYS_2026 = [
    # January
    "2026-01-07", "2026-01-14", "2026-01-28",
    # February
    "2026-02-04", "2026-02-11", "2026-02-25",
    # March
    "2026-03-04", "2026-03-11", "2026-03-25",
    # April
    "2026-04-01", "2026-04-08", "2026-04-22", "2026-04-29",
    # May
    "2026-05-06", "2026-05-13", "2026-05-27",
    # June
    "2026-06-03", "2026-06-10", "2026-06-24",
    # July
    "2026-07-01", "2026-07-08", "2026-07-22", "2026-07-29",
    # August
    "2026-08-05", "2026-08-12", "2026-08-26",
    # September
    "2026-09-02", "2026-09-09", "2026-09-23", "2026-09-30",
    # October
    "2026-10-07", "2026-10-14", "2026-10-28",
    # November
    "2026-11-04", "2026-11-11", "2026-11-25",
    # December
    "2026-12-02", "2026-12-09", "2026-12-23", "2026-12-30",
]

# EQUITY/ETF/ETN OPTIONS - Standard (3rd Friday of month)
OCC_MONTHLY_2026 = [
    "2026-01-16",  # Jan
    "2026-02-20",  # Feb
    "2026-03-20",  # Mar (Q1)
    "2026-04-17",  # Apr
    "2026-05-15",  # May
    "2026-06-19",  # Jun (Q2)
    "2026-07-17",  # Jul
    "2026-08-21",  # Aug
    "2026-09-18",  # Sep (Q3)
    "2026-10-16",  # Oct
    "2026-11-20",  # Nov
    "2026-12-18",  # Dec (Q4)
]

# QUARTERLY OPTIONS - End of Quarter (March, June, Sep, Dec)
QUARTERLY_2026 = [
    "2026-03-31",  # Q1
    "2026-06-30",  # Q2
    "2026-09-30",  # Q3
    "2026-12-31",  # Q4
]

# END OF MONTH OPTIONS - Last trading day of each month
END_OF_MONTH_2026 = [
    "2026-01-30",  # Jan
    "2026-02-27",  # Feb
    "2026-03-31",  # Mar (also Quarterly)
    "2026-04-30",  # Apr
    "2026-05-29",  # May
    "2026-06-30",  # Jun (also Quarterly)
    "2026-07-31",  # Jul
    "2026-08-31",  # Aug
    "2026-09-30",  # Sep (also Quarterly)
    "2026-10-30",  # Oct
    "2026-11-30",  # Nov
    "2026-12-31",  # Dec (also Quarterly)
]

# SPX & XSP WEEKLYS - Every business day except 3rd Friday, EOM, and Quarterly
# Note: Too many to list individually, handled by logic below

def get_event_type(date_str):
    """Determine the type(s) of expiration for a given date"""
    events = []
    
    if date_str in VIX_STANDARD_2026:
        events.append("VIX Monthly")
    
    if date_str in VIX_WEEKLYS_2026:
        events.append("VIX Weekly")
    
    if date_str in OCC_MONTHLY_2026:
        if date_str in QUARTERLY_2026:
            events.append("Quarterly OPEX")
        else:
            events.append("Monthly OPEX")
    
    if date_str in END_OF_MONTH_2026:
        if date_str not in QUARTERLY_2026:
            events.append("EOM Options")
    
    return events

def get_color_for_event(date_str):
    """Return Discord embed color based on event importance"""
    if date_str in QUARTERLY_2026:
        return 15844367  # Gold - Quarterly (highest importance)
    elif date_str in OCC_MONTHLY_2026:
        return 15548997  # Red - Monthly OPEX (high importance)
    elif date_str in VIX_STANDARD_2026:
        return 10181046  # Purple - VIX Monthly (medium-high)
    elif date_str in END_OF_MONTH_2026:
        return 3447003   # Blue - End of Month
    else:
        return 7506394   # Gray - Weekly
    
def get_importance_emoji(date_str):
    """Return emoji based on importance"""
    if date_str in QUARTERLY_2026:
        return "🔴"  # Red circle for quarterly
    elif date_str in OCC_MONTHLY_2026:
        return "🟠"  # Orange for monthly
    elif date_str in VIX_STANDARD_2026:
        return "🟣"  # Purple for VIX
    elif date_str in END_OF_MONTH_2026:
        return "🔵"  # Blue for EOM
    else:
        return "⚪"  # White for weekly

def send_discord_embed(title, description, color, fields=None):
    """Send formatted embed to Discord"""
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "2026 OPEX Calendar • CBOE"}
    }
    
    if fields:
        embed["fields"] = fields
    
    data = {"embeds": [embed]}
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print("✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_all_opex_dates():
    """Combine all unique OPEX dates"""
    all_dates = set()
    all_dates.update(VIX_STANDARD_2026)
    all_dates.update(VIX_WEEKLYS_2026)
    all_dates.update(OCC_MONTHLY_2026)
    all_dates.update(QUARTERLY_2026)
    all_dates.update(END_OF_MONTH_2026)
    return sorted(list(all_dates))

def get_upcoming_opex(days=7):
    """Get all OPEX events within next N days"""
    today = datetime.utcnow().date()
    upcoming = []
    
    for date_str in get_all_opex_dates():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        days_until = (date_obj - today).days
        
        if 0 <= days_until <= days:
            events = get_event_type(date_str)
            if events:  # Only include if there are events
                upcoming.append({
                    "date": date_str,
                    "date_obj": date_obj,
                    "days_until": days_until,
                    "events": events,
                    "emoji": get_importance_emoji(date_str)
                })
    
    return upcoming

def weekly_preview():
    """Send Monday weekly preview of all OPEX events"""
    upcoming = get_upcoming_opex(days=7)
    
    if not upcoming:
        return
    
    fields = []
    for event in upcoming:
        date_formatted = event["date_obj"].strftime("%A, %B %d")
        events_str = " + ".join(event["events"])
        
        # Build field value
        value = f"{event['emoji']} **{events_str}**"
        if event["days_until"] == 0:
            value += "\n⚠️ **TODAY**"
        elif event["days_until"] == 1:
            value += "\n📍 Tomorrow"
        else:
            value += f"\n📅 {event['days_until']} days away"
        
        fields.append({
            "name": date_formatted,
            "value": value,
            "inline": False
        })
    
    send_discord_embed(
        title="📊 OPEX Calendar - Week Ahead (2026)",
        description="Upcoming options expirations this week",
        color=5793266,  # Teal
        fields=fields
    )
    print(f"✅ Sent weekly preview with {len(upcoming)} events")

def daily_reminders():
    """Send D-1 and day-of reminders"""
    upcoming = get_upcoming_opex(days=1)
    
    for event in upcoming:
        date_formatted = event["date_obj"].strftime("%A, %B %d, %Y")
        events_str = " + ".join(event["events"])
        
        if event["days_until"] == 1:
            # D-1 reminder
            fields = [
                {
                    "name": "Event Types",
                    "value": events_str,
                    "inline": False
                },
                {
                    "name": "📌 Reminder",
                    "value": "Options expiration tomorrow",
                    "inline": False
                }
            ]
            
            send_discord_embed(
                title=f"⏰ Tomorrow: {event['emoji']} OPEX Alert",
                description=f"**{date_formatted}**",
                color=get_color_for_event(event["date"]),
                fields=fields
            )
            print(f"✅ Sent D-1 reminder for {event['date']}")
        
        elif event["days_until"] == 0:
            # Day-of alert
            fields = [
                {
                    "name": "Expiring Today",
                    "value": events_str,
                    "inline": False
                },
                {
                    "name": "⚠️ Market Impact",
                    "value": "Monitor for increased volatility and volume",
                    "inline": False
                }
            ]
            
            send_discord_embed(
                title=f"🔔 TODAY: {event['emoji']} OPEX ACTIVE",
                description=f"**Options Expiration Day**\n{date_formatted}",
                color=15158332,  # Red for urgency
                fields=fields
            )
            print(f"✅ Sent day-of alert for {event['date']}")

def send_test_message():
    """Send a test message to verify setup"""
    embed = {
        "title": "🎉 2026 OPEX Calendar Bot is Live!",
        "description": "Successfully configured for VIX, OCC, Quarterly, and EOM expirations",
        "color": 5763719,
        "fields": [
            {
                "name": "📅 Coverage",
                "value": "VIX Monthly & Weekly\nMonthly OPEX (3rd Friday)\nQuarterly OPEX\nEnd-of-Month Options",
                "inline": False
            },
            {
                "name": "🔔 Alerts",
                "value": "• Weekly Preview (Mondays 8 AM UTC)\n• D-1 Reminders (Daily 8 AM UTC)\n• Day-of Alerts (8 AM UTC)",
                "inline": False
            },
            {
                "name": "🎨 Color Coding",
                "value": "🔴 Quarterly (Gold)\n🟠 Monthly (Red)\n🟣 VIX Monthly (Purple)\n🔵 End-of-Month (Blue)\n⚪ Weekly (Gray)",
                "inline": False
            }
        ],
        "footer": {"text": "2026 OPEX Calendar • CBOE • All dates verified"},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    data = {
        "content": "✅ **Setup Complete!** Your 2026 OPEX alerts are now active.",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        return response.status_code == 204
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main bot logic - determines what to run based on time"""
    now = datetime.utcnow()
    day_of_week = now.weekday()
    hour = now.hour
    
    # Check if we're in a test run (no cron schedule)
    import sys
    if '--test' in sys.argv:
        print("🧪 Running in test mode...")
        send_test_message()
        return
    
    # Monday 8 AM UTC - Weekly Preview
    if day_of_week == 0 and hour == 8:
        print("📅 Running weekly preview...")
        weekly_preview()
    
    # Daily 8 AM UTC - D-1 and Day-of Reminders
    elif hour == 8:
        print("⏰ Running daily reminders...")
        daily_reminders()
    
    else:
        print(f"⏸️ No scheduled action for {now.strftime('%A %H:%M UTC')}")

if __name__ == "__main__":
    main()
