import requests
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ======================
# CONFIGURATION
# ======================

API_KEY = "a9badbfcc033516c940caa12ca5705ca"  # Your API key
EMAIL_ADDRESS = "gregory.mwangi3@gmail.com"   # Your email
EMAIL_PASSWORD = "gmabsistfpiksqbi"           # Your App password

API_KEY = "Your API key"  # Your API key
EMAIL_ADDRESS = " Your email"   # Your email
EMAIL_PASSWORD = "Your App password"           # Your App password

BASE_URL = "https://v3.football.api-sports.io"
SEASON = datetime.now().year
HEADERS = {"x-apisports-key": API_KEY}

# Date setup
today = datetime.now().date()
tomorrow = today + timedelta(days=1)

# ======================
# LEAGUE SELECTION
# ======================
LEAGUES = {
    # Europe (Top-Tier)
    "Premier League (England)": 39,
    "La Liga (Spain)": 140,
    "Bundesliga (Germany)": 78,
    "Serie A (Italy)": 135,
    "Ligue 1 (France)": 61,
    "Primeira Liga (Portugal)": 94,
    "Eredivisie (Netherlands)": 88,
    "Belgian Pro League (Belgium)": 144,
    "Scottish Premiership (Scotland)": 179,
    "Süper Lig (Turkey)": 203,
    "Russian Premier League (Russia)": 235,
    "Ukrainian Premier League (Ukraine)": 332,
    "Austrian Bundesliga (Austria)": 218,
    "Danish Superliga (Denmark)": 119,
    "Swiss Super League (Switzerland)": 207,
    "Norwegian Eliteserien (Norway)": 113,
    "Swedish Allsvenskan (Sweden)": 129,
    "Finnish Veikkausliiga (Finland)": 106,
    "Polish Ekstraklasa (Poland)": 106,
    "Czech First League (Czech Republic)": 319,
    "Super Liga (Slovakia)": 333,
    "Croatian HNL (Croatia)": 210,
    "Serbian SuperLiga (Serbia)": 238,
    "Liga I (Romania)": 239,
    "Greek Super League (Greece)": 197,

    # Americas (Top-Tier)
    "MLS (USA)": 253,
    "Liga MX (Mexico)": 262,
    "Brasileirão (Brazil)": 71,
    "Argentine Primera División (Argentina)": 128,
    "Liga Profesional (Colombia)": 239,  # Note: Shared ID (verify)
    "Primera División (Chile)": 239,    # Note: Shared ID (verify)

    # Asia/Africa (Top-Tier)
    "Saudi Pro League (Saudi Arabia)": 350,
    "J1 League (Japan)": 98,
    "Chinese Super League (China)": 169,
    "A-League (Australia)": 1,
    "K League 1 (South Korea)": 292,
    "Egyptian Premier League (Egypt)": 308,
    "South African PSL (South Africa)": 384,
    "Indian Super League (India)": 322,

    # Second Divisions (Tier 2)
    "Championship (England)": 40,
    "La Liga 2 (Spain)": 141,
    "2. Bundesliga (Germany)": 79,
    "Serie B (Italy)": 136,
    "Ligue 2 (France)": 62,
    "Segunda Liga (Portugal)": 95,
    "Eerste Divisie (Netherlands)": 89,
    "Challenger Pro League (Belgium)": 145,
    "Superettan (Sweden)": 130,
    "2. Liga (Austria)": 219,
    "Serie B (Brazil)": 72,

    # Third Divisions (Tier 3)
    "League One (England)": 41,
    "Primera RFEF (Spain)": 142,
    "Serie C (Italy)": 137,
    "National (France)": 63,
    "3. Liga (Germany)": 80,

    # Other Notable Leagues
    "USL Championship (USA)": 254,
    "Canadian Premier League (Canada)": 254,  # Same as USL (verify)
    "Liga MX Expansion (Mexico)": 263,
}

# ======================
# HELPER FUNCTION (with retries)
# ======================
def safe_request(url, retries=3, timeout=15):
    """Wrapper for requests with retries"""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print(f"⏳ Timeout, retrying {attempt+1}/{retries}...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Request error: {str(e)}")
            return {}
    return {}

# ======================
# CORE FUNCTIONS
# ======================
def get_top_8_teams(league_id):
    url = f"{BASE_URL}/standings?league={league_id}&season={SEASON}"
    data = safe_request(url)
    if data.get("response"):
        standings = data["response"][0]["league"]["standings"][0][:8]
        return {team["team"]["id"]: team["team"]["name"] for team in standings}
    return {}

def get_last_2_matches(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&last=2&status=FT"
    data = safe_request(url)
    return data.get("response", [])

def has_goalless_streak(matches, team_id):
    if len(matches) < 2:
        return False
    return all(
        (match["goals"]["home"] if match["teams"]["home"]["id"] == team_id else match["goals"]["away"]) == 0
        for match in matches
    )

def get_upcoming_match(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&next=1"
    data = safe_request(url)
    if data.get("response"):
        match = data["response"][0]
        match_date = datetime.strptime(match["fixture"]["date"][:10], "%Y-%m-%d").date()
        if match_date in [today, tomorrow]:
            return match
    return None

def send_email(subject, body):
    """Send results via email"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("\n📧 Email sent successfully!")
    except Exception as e:
        print(f"🚨 Failed to send email: {str(e)}")

# ======================
# MAIN EXECUTION
# ======================
def main():
    print(f"\n🔍 Scanning {len(LEAGUES)} leagues for teams with:")
    print("- Top 8 in their league")
    print("- 0 goals in last 2 matches")
    print("- Playing today or tomorrow\n")

    results = []

    for league_name, league_id in LEAGUES.items():
        teams = get_top_8_teams(league_id)
        time.sleep(1)

        if not teams:
            continue

        league_results = []

        for team_id, team_name in teams.items():
            matches = get_last_2_matches(team_id)
            time.sleep(1)

            if has_goalless_streak(matches, team_id):
                next_match = get_upcoming_match(team_id)
                time.sleep(1)

                if next_match:
                    is_home = next_match["teams"]["home"]["id"] == team_id
                    details = {
                        "team": team_name,
                        "opponent": next_match["teams"]["away"]["name"] if is_home else next_match["teams"]["home"]["name"],
                        "date": next_match["fixture"]["date"][:10],
                        "time": next_match["fixture"]["date"][11:16],
                        "venue": "Home" if is_home else "Away"
                    }
                    league_results.append(details)

        if league_results:
            results.append({"league": league_name, "matches": league_results})

    # Build email body
    if results:
        email_body = "📊 MATCHES FOUND:\n\n"
        for league in results:
            email_body += f"🏆 {league['league']}\n"
            for match in league["matches"]:
                email_body += f"  🔴 {match['team']} (Last 2: 0 goals)\n"
                email_body += f"    ⏩ {match['date']} at {match['time']} vs {match['opponent']} ({match['venue']})\n"
            email_body += "\n"
    else:
        email_body = "ℹ️ No qualifying matches found."

    print("\n" + email_body)
    send_email("⚽ Football Report - Teams With 0 Goals in Last 2 Matches", email_body)
    print(f"\n✅ Completed scan of {len(LEAGUES)} leagues")

if __name__ == "__main__":
    main()
