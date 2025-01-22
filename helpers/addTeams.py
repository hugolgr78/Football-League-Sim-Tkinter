import json

# Define the Premier League teams for the 22/23 season
premier_league_teams = [
    {"name": "Manchester City", "level": 200, "stadium": "Etihad Stadium"},
    {"name": "Arsenal", "level": 200, "stadium": "Emirates Stadium"},
    {"name": "Liverpool", "level": 200, "stadium": "Anfield"},
    {"name": "Aston Villa", "level": 200, "stadium": "Villa Park"},
    {"name": "Tottenham", "level": 200, "stadium": "Tottenham Hotspur Stadium"},
    {"name": "Chelsea", "level": 200, "stadium": "Stamford Bridge"},
    {"name": "Newcastle United", "level": 200, "stadium": "St James' Park"},
    {"name": "Manchester United", "level": 200, "stadium": "Old Trafford"},
    {"name": "West Ham", "level": 200, "stadium": "London Stadium"},
    {"name": "Crystal Palace", "level": 200, "stadium": "Selhurst Park"},
    {"name": "Brighton", "level": 200, "stadium": "Amex Stadium"},
    {"name": "Bournemouth", "level": 200, "stadium": "Vitality Stadium"},
    {"name": "Fulham", "level": 200, "stadium": "Craven Cottage"},
    {"name": "Wolves", "level": 200, "stadium": "Molineux Stadium"},
    {"name": "Everton", "level": 200, "stadium": "Goodison Park"},
    {"name": "Brentford", "level": 200, "stadium": "Brentford Community Stadium"},
    {"name": "Nottingham Forest", "level": 200, "stadium": "City Ground"},
    {"name": "Luton Town", "level": 200, "stadium": "Kenilworth Road"},
    {"name": "Burnley", "level": 200, "stadium": "Turf Moor"},
    {"name": "Sheffield United", "level": 200, "stadium": "Bramall Lane"},
    {"name": "Paris Saint-Germain", "level": 200, "stadium": "Parc des Princes"},
]

# Create a list of dictionaries for each team respecting the provided structure
teams_data = []
for team in premier_league_teams:
    team_data = {
        "name": team["name"],
        "level": team["level"],
        "stadium": team["stadium"],
        "logoPath": "SavedImages/Teams/" + team["name"] + ".png",
        "competitions": [],
    }
    teams_data.append(team_data)

# Write the data to a JSON file
with open('teams.json', 'w') as file:
    json.dump(teams_data, file, indent=4)