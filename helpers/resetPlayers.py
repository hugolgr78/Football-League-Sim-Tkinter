import json
from faker import Faker
import random
from settings import *

fake = Faker()

# Load the teams data from the JSON file
with open('./players.json', 'r') as f:
    teams = json.load(f)

# Populate the "players" field for each team
for team in teams:
    players = []
    for i in range(24):
        name = fake.name_male()
        name = name.replace("Mr. ", "").replace("Dr. ", "").replace(" PhD", "").replace(" MD", "").replace(" DVM", "").replace(" DDS", "")

        if i < 3:
            position = "goalkeeper"
            gkChances = [0.9, 0.05, 0.05]
            gkNumbers = [1, 16, 99]
            chance = gkChances[i]
            number = gkNumbers[i]
        elif i < 11:
            position = "defender"
            defChances = [0.7, 0.71, 0.72, 0.69, 0.3, 0.29, 0.28, 0.31]
            defNumbers = [2, 3, 4, 5, 6, 17, 21, 22]
            chance = defChances[i - 3]
            number = defNumbers[i - 3]
        elif i < 17:
            position = "midfielder"
            midChances = [0.7, 0.71, 0.69, 0.3, 0.31, 0.29]
            midNumbers = [8, 10, 13, 14, 15, 16]
            chance = midChances[i - 11]
            number = midNumbers[i - 11]
        else:
            position = "forward"
            fwdChances = [0.8, 0.7, 0.71, 0.3, 0.29, 0.1, 0.1]
            fwdNumbers = [7, 9, 11, 24, 25, 26, 30]
            chance = fwdChances[i - 17]
            number = fwdNumbers[i - 17]

        selectedContinent = random.choices(list(continentWeights.keys()), weights=list(continentWeights.values()), k=1)[0]
        continent, countryWeights = COUNTRIES[selectedContinent]
        country = random.choices(list(countryWeights.keys()), weights=list(countryWeights.values()), k=1)[0]
        
        player = {
            "name": name,
            "age": random.randint(18, 35),
            "number": number,
            "nationality": country,
            "position": position,
            "startingChance": chance,
            "seasonStats": [],
            "matchBan": [],
            "matches": [],
            "seasonsData": [],
            "trophies": {}
        }
            
        players.append(player)
    
    team['players'] = players

# Save the updated teams data back to the JSON file
with open('./players.json', 'w') as f:
    json.dump(teams, f, indent=4)