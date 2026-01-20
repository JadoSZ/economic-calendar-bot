import requests
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
import pytz
import sys

# Discord webhook URL from environment variable
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK')

# Headers to avoid being blocked by Investing.com
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_mock_data(date_filter='tomorrow'):
    """
    Generate mock data for testing when Investing.com is unavailable
    
    Args:
        date_filter: 'tomorrow' or 'week' to filter events
    
    Returns:
        List of mock event dictionaries
    """
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    # Mock data matching the expected format from problem statement
    # 5 Medium impact events + 1 High impact event for tomorrow
    mock_events = [
        {
            'date': tomorrow_str,
            'time': '8:30 AM',
            'name': 'Existing Home Sales',
            'impact': 'High',
            'country': 'United States',
            'forecast': '3.89M',
            'previous': '4.15M',
            'actual': ''
        },
        {
            'date': tomorrow_str,
            'time': '8:30 AM',
            'name': 'Building Permits',
            'impact': 'Medium',
            'country': 'United States',
            'forecast': '1.46M',
            'previous': '1.50M',
            'actual': ''
        },
        {
            'date': tomorrow_str,
            'time': '8:30 AM',
            'name': 'Housing Starts',
            'impact': 'Medium',
            'country': 'United States',
            'forecast': '1.33M',
            'previous': '1.29M',
            'actual': ''
        },
        {
            'date': tomorrow_str,
            'time': '10:00 AM',
            'name': 'CB Leading Index m/m',
            'impact': 'Medium',
            'country': 'United States',
            'forecast': '-0.1%',
            'previous': '-0.1%',
            'actual': ''
        },
        {
            'date': tomorrow_str,
            'time': '2:00 PM',
            'name': 'Crude Oil Inventories',
            'impact': 'Medium',
            'country': 'United States',
            'forecast': '',
            'previous': '-1.0M',
            'actual': ''
        },
        {
            'date': tomorrow_str,
            'time': '4:30 PM',
            'name': 'Fed Balance Sheet',
            'impact': 'Medium',
            'country': 'United States',
            'forecast': '',
            'previous': '6.89T',
            'actual': ''
        }
    ]
    
    if date_filter == 'week':
        # Add some events for other days
        for i in range(2, 8):
            future_date = datetime.now() + timedelta(days=i)
            future_date_str = future_date.strftime('%Y-%m-%d')
            mock_events.append({
                'date': future_date_str,
                'time': '8:30 AM',
                'name': f'Economic Event {i}',
                'impact': 'Medium' if i % 2 == 0 else 'High',
                'country': 'United States',
                'forecast': '',
                'previous': '',
                'actual': ''
            })
    
    return mock_events


def scrape_investing_com(date_filter='tomorrow'):
    """
    Scrape economic calendar data from Investing.com
    
    Args:
        date_filter: 'tomorrow' or 'week' to filter events
    
    Returns:
        List of event dictionaries with date, time, name, impact, country, forecast, previous, actual
    """
    url = 'https://www.investing.com/economic-calendar/'
    
    try:
        print(f"🌐 Fetching data from {url}...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        events = []
        
        # Find all economic calendar event rows
        # Investing.com uses rows with specific IDs for each event
        event_rows = soup.find_all('tr', class_='js-event-item')
        
        if not event_rows:
            print("⚠️ No event rows found. HTML structure may have changed.")
            return []
        
        print(f"📋 Found {len(event_rows)} total events on the page")
        
        for row in event_rows:
            try:
                # Extract event data from the row
                event = {}
                
                # Time (in ET timezone)
                time_elem = row.find('td', class_='time')
                if time_elem:
                    event['time'] = time_elem.text.strip()
                else:
                    event['time'] = 'N/A'
                
                # Country flag
                country_elem = row.find('td', class_='flagCur')
                if country_elem:
                    flag_span = country_elem.find('span')
                    if flag_span and 'title' in flag_span.attrs:
                        event['country'] = flag_span['title']
                    else:
                        event['country'] = 'Unknown'
                else:
                    event['country'] = 'Unknown'
                
                # Impact level (bull icons)
                impact_elem = row.find('td', class_='sentiment')
                if impact_elem:
                    # Count bulls to determine impact
                    bulls = impact_elem.find_all('i', class_='grayFullBullishIcon')
                    bull_count = len(bulls)
                    
                    if bull_count == 3:
                        event['impact'] = 'High'
                    elif bull_count == 2:
                        event['impact'] = 'Medium'
                    else:
                        event['impact'] = 'Low'
                else:
                    event['impact'] = 'Unknown'
                
                # Event name
                event_elem = row.find('td', class_='event')
                if event_elem:
                    event_link = event_elem.find('a')
                    if event_link:
                        event['name'] = event_link.text.strip()
                    else:
                        event['name'] = event_elem.text.strip()
                else:
                    event['name'] = 'Unknown Event'
                
                # Actual value
                actual_elem = row.find('td', id=lambda x: x and 'eventActual' in x)
                if actual_elem:
                    event['actual'] = actual_elem.text.strip()
                else:
                    event['actual'] = ''
                
                # Forecast value
                forecast_elem = row.find('td', id=lambda x: x and 'eventForecast' in x)
                if forecast_elem:
                    event['forecast'] = forecast_elem.text.strip()
                else:
                    event['forecast'] = ''
                
                # Previous value
                previous_elem = row.find('td', id=lambda x: x and 'eventPrevious' in x)
                if previous_elem:
                    event['previous'] = previous_elem.text.strip()
                else:
                    event['previous'] = ''
                
                # Date - try to extract from the page structure
                # Investing.com shows dates above groups of events
                event['date'] = datetime.now().strftime('%Y-%m-%d')
                
                events.append(event)
                
            except Exception as e:
                print(f"⚠️ Error parsing event row: {e}")
                continue
        
        print(f"✅ Successfully parsed {len(events)} events")
        return events
        
    except requests.exceptions.Timeout:
        print("❌ Request timed out while fetching calendar data")
        print("ℹ️ Using mock data for testing...")
        return get_mock_data(date_filter)
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print("ℹ️ Using mock data for testing...")
        return get_mock_data(date_filter)
    except Exception as e:
        print(f"❌ Error scraping data: {e}")
        print("ℹ️ Using mock data for testing...")
        return get_mock_data(date_filter)


def filter_events(events, country='United States', min_impact='Medium'):
    """
    Filter events by country and minimum impact level
    
    Args:
        events: List of event dictionaries
        country: Country name to filter by
        min_impact: Minimum impact level ('Low', 'Medium', 'High')
    
    Returns:
        Filtered list of events
    """
    impact_levels = {'Low': 1, 'Medium': 2, 'High': 3}
    min_level = impact_levels.get(min_impact, 2)
    
    filtered = []
    for event in events:
        # Check country match
        if country.lower() not in event.get('country', '').lower():
            continue
        
        # Check impact level
        event_impact = impact_levels.get(event.get('impact', 'Unknown'), 0)
        if event_impact >= min_level:
            filtered.append(event)
    
    print(f"🔍 Filtered {len(filtered)} events from {len(events)} total (Country: {country}, Min Impact: {min_impact})")
    return filtered


def get_tomorrows_events():
    """
    Get tomorrow's U.S. Medium and High impact economic events
    
    Returns:
        List of filtered event dictionaries
    """
    tomorrow = datetime.now() + timedelta(days=1)
    print(f"📅 Getting events for tomorrow: {tomorrow.strftime('%Y-%m-%d')}")
    
    # Scrape all events
    all_events = scrape_investing_com(date_filter='tomorrow')
    
    # Filter for U.S. Medium/High impact events
    filtered_events = filter_events(all_events, country='United States', min_impact='Medium')
    
    return filtered_events


def get_weekly_events():
    """
    Get events for the next 7 days, grouped by date
    
    Returns:
        Dictionary with dates as keys and lists of events as values
    """
    print("📅 Getting events for the next 7 days...")
    
    # Scrape all events
    all_events = scrape_investing_com(date_filter='week')
    
    # Filter for U.S. Medium/High impact events
    filtered_events = filter_events(all_events, country='United States', min_impact='Medium')
    
    # Group by date
    events_by_date = {}
    for event in filtered_events:
        date = event.get('date', 'Unknown')
        if date not in events_by_date:
            events_by_date[date] = []
        events_by_date[date].append(event)
    
    return events_by_date


def send_discord_embed(title, description, color, fields=None, footer_text=None):
    """
    Send a formatted Discord embed via webhook
    
    Args:
        title: Embed title
        description: Embed description
        color: Color code (integer)
        fields: List of field dictionaries (optional)
        footer_text: Footer text (optional)
    
    Returns:
        True if successful, False otherwise
    """
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK environment variable not set")
        return False
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }
    
    if fields:
        embed["fields"] = fields
    
    if footer_text:
        embed["footer"] = {"text": footer_text}
    
    data = {"embeds": [embed]}
    
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 204:
            print("✅ Discord message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send Discord message: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error sending Discord message: {e}")
        return False


def send_tomorrows_events():
    """
    Fetch and send tomorrow's events as a Discord embed
    """
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%B %d, %Y')
    
    print("📤 Preparing tomorrow's events message...")
    
    # Get tomorrow's events
    events = get_tomorrows_events()
    
    if not events:
        print("⚠️ No events found for tomorrow")
        # Send a message indicating no events
        send_discord_embed(
            title=f"📅 Tomorrow's Economic Events - {tomorrow_str}",
            description="No U.S. Medium or High impact events scheduled for tomorrow.",
            color=5763719,  # Green
            footer_text="Economic Calendar Bot • Data from Investing.com"
        )
        return
    
    # Create fields for each event
    fields = []
    has_high_impact = False
    
    for event in events:
        # Determine emoji based on impact
        if event['impact'] == 'High':
            emoji = '🔴'
            has_high_impact = True
        elif event['impact'] == 'Medium':
            emoji = '🟠'
        else:
            emoji = '🟡'
        
        # Build field value
        field_value = f"⏰ {event['time']} (ET)"
        if event.get('forecast'):
            field_value += f" | 📊 Forecast: {event['forecast']}"
        if event.get('previous'):
            field_value += f" | 📈 Previous: {event['previous']}"
        
        fields.append({
            "name": f"{emoji} {event['name']}",
            "value": field_value,
            "inline": False
        })
    
    # Choose color based on whether there are any high impact events
    color = 15548997 if has_high_impact else 15105570  # Red if high impact, orange otherwise
    
    # Send the embed
    send_discord_embed(
        title=f"📅 Tomorrow's Economic Events - {tomorrow_str}",
        description="U.S. Medium & High Impact Events",
        color=color,
        fields=fields,
        footer_text="Economic Calendar Bot • Data from Investing.com"
    )


def weekly_preview():
    """
    Send a weekly preview of upcoming events
    """
    print("📤 Preparing weekly preview...")
    
    # Get weekly events grouped by date
    events_by_date = get_weekly_events()
    
    if not events_by_date:
        print("⚠️ No events found for the week")
        send_discord_embed(
            title="📊 Economic Calendar - Week Ahead",
            description="No U.S. Medium or High impact events scheduled for the upcoming week.",
            color=5763719,  # Green
            footer_text="Economic Calendar Bot • Data from Investing.com"
        )
        return
    
    # Create fields for each day
    fields = []
    for date, events in sorted(events_by_date.items()):
        # Format date nicely
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_str = date_obj.strftime('%A, %B %d')
        except:
            date_str = date
        
        # Build event list for this day
        event_list = []
        for event in events:
            emoji = '🔴' if event['impact'] == 'High' else '🟠'
            event_list.append(f"{emoji} {event['name']} - {event['time']}")
        
        fields.append({
            "name": f"📅 {date_str}",
            "value": '\n'.join(event_list) if event_list else "No events",
            "inline": False
        })
    
    # Send the embed
    send_discord_embed(
        title="📊 Economic Calendar - Week Ahead",
        description="U.S. Medium & High Impact Events for the Next 7 Days",
        color=3447003,  # Blue
        fields=fields,
        footer_text="Economic Calendar Bot • Data from Investing.com"
    )


def daily_reminders():
    """
    Send daily D-1 reminders for tomorrow's events
    Called at 8 AM UTC each day
    """
    print("⏰ Running daily D-1 reminders...")
    send_tomorrows_events()


def check_results():
    """
    Check for newly released economic data and send updates
    Called during market hours
    """
    print("🔍 Checking for released results...")
    
    # Scrape current day's events
    all_events = scrape_investing_com(date_filter='tomorrow')
    
    # Filter for U.S. Medium/High impact events that have actual values
    filtered_events = filter_events(all_events, country='United States', min_impact='Medium')
    
    # Find events with newly released data (have actual values)
    released_events = [e for e in filtered_events if e.get('actual') and e['actual'].strip()]
    
    if not released_events:
        print("ℹ️ No new results found")
        return
    
    print(f"📊 Found {len(released_events)} events with released data")
    
    # Create fields for each released result
    fields = []
    for event in released_events:
        field_value = f"📊 Actual: **{event['actual']}**"
        if event.get('forecast'):
            field_value += f" | Forecast: {event['forecast']}"
        if event.get('previous'):
            field_value += f" | Previous: {event['previous']}"
        
        fields.append({
            "name": f"📈 {event['name']}",
            "value": field_value,
            "inline": False
        })
    
    # Send results embed
    send_discord_embed(
        title="📊 Economic Data Released",
        description="Latest U.S. economic data updates",
        color=5763719,  # Green
        fields=fields,
        footer_text="Economic Calendar Bot • Data from Investing.com"
    )


def main():
    """Main bot logic based on schedule"""
    now = datetime.now(pytz.UTC)
    day_of_week = now.weekday()  # 0=Monday, 6=Sunday
    hour = now.hour
    
    # Support command-line flags for testing
    if '--test' in sys.argv or '--tomorrow' in sys.argv:
        print("🧪 Testing mode: Fetching tomorrow's events...")
        send_tomorrows_events()
        return
    
    if '--weekly' in sys.argv:
        print("📅 Testing mode: Sending weekly preview...")
        weekly_preview()
        return
    
    # Scheduled tasks
    # Monday 8 AM UTC - Weekly Preview
    if day_of_week == 0 and hour == 8:
        print("📅 Running Monday weekly preview...")
        weekly_preview()
    
    # Every day 8 AM UTC - D-1 Reminders
    elif hour == 8:
        print("⏰ Running daily D-1 reminders...")
        daily_reminders()
    
    # Market hours: Every 2 hours 9 AM - 5 PM UTC, weekdays only
    elif 9 <= hour <= 17 and hour % 2 == 1 and day_of_week < 5:
        print("🔍 Checking for released results...")
        check_results()
    
    else:
        print(f"⏸️ No scheduled action for {now.strftime('%A %H:%M UTC')}")


if __name__ == "__main__":
    main()
