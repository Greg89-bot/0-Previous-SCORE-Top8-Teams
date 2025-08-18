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
EMAIL_PASSWORD = "bvvibaknyysmthww"           # Your App password
BASE_URL = "https://v3.football.api-sports.io"
SEASON = datetime.now().year
HEADERS = {"x-apisports-key": API_KEY}

# Date setup
today = datetime.now().date()
tomorrow = today + timedelta(days=1)

# ======================
# LEAGUE SELECTION (40+ leagues)
# ======================
LEAGUES = {
    # Top European Leagues (Tier 1)
    "Premier League": 39, "Serie A": 135, "Bundesliga": 78,
    "La Liga": 140, "Ligue 1": 61, "Primeira Liga": 94,
    "Eredivisie": 88, "Belgian Pro League": 144,
    "Scottish Premiership": 179, "Turkish Süper Lig": 203,
    "Russian Premier League": 235, "Ukrainian Premier League": 332,
    "Austrian Bundesliga": 218, "Danish Superliga": 119,
    "Swiss Super League": 207, "Norwegian Eliteserien": 113,
    "Swedish Allsvenskan": 129, "Finnish Veikkausliiga": 106,
    "Polish Ekstraklasa": 106, "Greek Super League": 197,

    # Second Divisions (Tier 2)
    "Championship": 40, "Serie B": 136, "2. Bundesliga": 79,
    "La Liga 2": 141, "Ligue 2": 62, "Challenger Pro League": 145,
    "Segunda Liga": 95, "Eerste Divisie": 89,
    "Scottish Championship": 180, "TFF First League": 204,
    "RFNL (Russia)": 236, "Liga 2 (Romania)": 239,
    "Super League Greece 2": 197, "Liga Portugal 2": 95,
    "Serie B (Brazil)": 72, "USL Championship (USA)": 254,

    # Third Divisions (Tier 3)
    "League One": 41, "Serie C": 137, "3. Liga": 80,
    "Primera RFEF": 142, "National": 63, "Scottish League One": 181,
    "Liga 3 (Portugal)": 96, "Serie C (Brazil)": 73,
    "USL League One (USA)": 255, "Liga Premier (Mexico)": 263,

    # Other Notable Leagues
    "MLS": 253, "Liga MX": 262, "Brazilian Serie A": 71,
    "Argentine Primera Division": 128, "Saudi Pro League": 239,
    "J1 League": 98, "Chinese Super League": 169,
    "A-League (Australia)": 1, "K League 1 (South Korea)": 292,

    # Additional European Lower Leagues
    "League Two": 42, "Serie D": 137, "Regionalliga": 81,
    "Serie D (Italy)": 138, "Nationwide Division (Greece)": 198,
    "Liga 3 (Spain)": 143, "Liga 3 (Germany)": 82,

    # Scandinavian Lower Leagues
    "1. Division (Denmark)": 120, "Superettan (Sweden)": 130,
    "OBOS-ligaen (Norway)": 114, "Ykkönen (Finland)": 107,

    # Additional Americas Leagues
    "Liga Profesional (Colombia)": 239, "Primera Division (Chile)": 239,
    "Liga 1 (Peru)": 239, "Liga Pro (Ecuador)": 239
}

# ======================
# CORE FUNCTIONS
# ======================

def get_top_8_teams(league_id):
    url = f"{BASE_URL}/standings?league={league_id}&season={SEASON}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        if data.get("response"):
            standings = data["response"][0]["league"]["standings"][0][:8]
            return {team["team"]["id"]: team["team"]["name"] for team in standings}
    except Exception as e:
        print(f"⚠️ Error getting standings for league {league_id}: {str(e)}")
    return {}

def get_last_2_matches(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&last=2&status=FT"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.json().get("response", [])
    except Exception as e:
        print(f"⚠️ Error getting matches for team {team_id}: {str(e)}")
    return []

def has_goalless_streak(matches, team_id):
    if len(matches) < 2:
        return False
    return all(
        (match["goals"]["home"] if match["teams"]["home"]["id"] == team_id else match["goals"]["away"]) == 0
        for match in matches
    )

def get_upcoming_match(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&next=1"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.json().get("response"):
            match = response.json()["response"][0]
            match_date = datetime.strptime(match["fixture"]["date"][:10], "%Y-%m-%d").date()
            if match_date in [today, tomorrow]:
                return match
    except Exception as e:
        print(f"⚠️ Error getting next match for team {team_id}: {str(e)}")
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
        try:
            teams = get_top_8_teams(league_id)
            time.sleep(1)

            if not teams:
                continue

            league_results = []

            for team_id, team_name in teams.items():
                try:
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

                except Exception as e:
                    print(f"  ⚠️ Error processing {team_name}: {str(e)}")
                    continue

            if league_results:
                results.append({
                    "league": league_name,
                    "matches": league_results
                })

        except Exception as e:
            print(f"🚨 Error processing {league_name}: {str(e)}")
            continue

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
