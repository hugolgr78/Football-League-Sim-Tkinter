import json

# Load the data from the JSON file
with open('./teams.json', 'r') as f:
    data = json.load(f)

# Update the 'amtchban' field for each player
for team in data:
    for player in team['players']:
        player['matchBan'] = 0

# Write the updated data back to the JSON file
with open('./teams.json', 'w') as f:
    json.dump(data, f, indent=4)