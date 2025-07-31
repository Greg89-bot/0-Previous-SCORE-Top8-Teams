import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import time

# === CONFIGURATION ===
API_KEY = "a9badbfcc033516c940caa12ca5705ca"  # Your API key
EMAIL_ADDRESS = "gregory.mwangi3@gmail.com"   # Your email
EMAIL_PASSWORD = "qwdidcxpnknfeasv"           # Gmail app password

LEAGUES = {
    "Premier League": 39,
    "Serie A": 135,
    "Bundesliga": 78,
    "La Liga": 140,
    "Ligue 1": 61,
    "Primeira Liga": 94,
}

HEADERS = {
    "x-apisports-key": API_KEY
}

today = datetime.today()
report_date = today.strftime('%d %B %Y')

# === FUNCTIONS ===
def get_top_8_teams(league_id):
    url = f"https://v3.football.api-sports.io/standings?league={league_id}&season=2023"
    res = requests.get(url, headers=HEADERS)
    json_data = res.json()
    if 'response' not in json_data or not json_data['response']:
        raise Exception(f"Error fetching standings: {json_data}")
    standings = json_data['response'][0]['league']['standings'][0]
    top_teams = standings[:8]
    return [team['team']['id'] for team in top_teams], {team['team']['id']: team['team']['name'] for team in top_teams}

def get_last_2_matches(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&season=2023&status=FT"
    res = requests.get(url, headers=HEADERS)
    json_data = res.json()
    if 'response' not in json_data or not json_data['response']:
        raise Exception(f"Error fetching fixtures: {json_data}")
    return sorted(json_data['response'], key=lambda x: x['fixture']['date'], reverse=True)[:2]

def get_zero_goal_match_info(matches, team_id):
    zero_goal_info = []
    for match in matches:
        is_home = match['teams']['home']['id'] == team_id
        opponent = match['teams']['away']['name'] if is_home else match['teams']['home']['name']
        goals_for = match['goals']['home'] if is_home else match['goals']['away']
        goals_against = match['goals']['away'] if is_home else match['goals']['home']
        venue = "Home" if is_home else "Away"
        date = match['fixture']['date'][:10]

        if goals_for == 0:
            zero_goal_info.append(f"{goals_for}-{goals_against} vs {opponent} ({venue}) on {date}")
    return zero_goal_info

def send_email(subject, body):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())

# === MAIN SCRIPT ===
email_body = f"<h2>⚽ Football Report for {report_date}</h2>"

for league_name, league_id in LEAGUES.items():
    try:
        print(f"🔍 Checking {league_name}...")
        top_ids, name_map = get_top_8_teams(league_id)
        time.sleep(6)

        no_score_teams = {}

        for team_id in top_ids:
            try:
                matches = get_last_2_matches(team_id)
                time.sleep(6)
                zero_info = get_zero_goal_match_info(matches, team_id)
                if zero_info:
                    no_score_teams[name_map[team_id]] = zero_info
            except Exception as e:
                print(f"⚠️ Error fetching team {team_id}: {e}")

        if no_score_teams:
            email_body += f"<h3>{league_name}</h3><ul>"
            for team, details in no_score_teams.items():
                email_body += f"<li>{team}<ul>"
                for detail in details:
                    email_body += f"<li style='font-size:90%;color:gray'>{detail}</li>"
                email_body += "</ul></li>"
            email_body += "</ul>"

    except Exception as e:
        email_body += f"<p><b>Error fetching {league_name}:</b> {e}</p>"

email_body += f"<hr><p style='font-size:small;color:gray;'>Sent by Football Script v2.0 — {report_date}</p>"

# === SEND EMAIL ===
print("📧 Sending email...")
send_email("⚽ Football Report - Teams That Failed to Score (Detail)", email_body)
print("✅ Email sent successfully!")
# Graceful exit
import sys
sys.exit(0)
