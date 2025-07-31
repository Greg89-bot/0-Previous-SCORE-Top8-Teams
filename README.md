# ⚽ 0-Previous SCORE - Top 8 Teams Performance

This Python script generates a weekly report showing football teams from top European leagues that **failed to score** in their last two matches. The script uses the [API-Football](https://www.api-football.com/) API to fetch live standings and fixtures, checks each top 8 team, and sends an HTML email with a summary of non-scoring teams.

## 📌 Features
- Checks **top 8 teams** in:
  - Premier League
  - Serie A
  - Bundesliga
  - La Liga
  - Ligue 1
  - Primeira Liga
- Highlights teams that **scored 0 goals** in their last 1 or 2 matches
- Sends a well-formatted HTML report to your email
