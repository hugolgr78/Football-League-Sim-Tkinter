import json

# Load the JSON data from the file
with open('./leaguesData.json', 'r') as file:
    data = json.load(file)

injuries_not_none_count = 0

# Iterate through the data to count instances
for league in data:
    for matchDay in league["matchDays"]:
        for match in matchDay["matches"]:
            if match['injured'] != "none":
                injuries_not_none_count += 1

print(f"Injuries Count: {injuries_not_none_count}")