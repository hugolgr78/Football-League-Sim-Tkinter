import json

# Load the JSON data from the file
with open('./players.json', 'r') as file:
    data = json.load(file)

# Initialize a dictionary to hold the count of players from each country
country_player_count = {}

# Iterate through the data to count players from each country
for team in data:
    for player in team['players']:
        country = player['nationality']
        if country in country_player_count:
            country_player_count[country] += 1
        else:
            country_player_count[country] = 1

# Sort the country_player_count dictionary by count in descending order
sorted_country_player_count = sorted(country_player_count.items(), key=lambda x: x[1], reverse=True)

# Print the sorted count of players from each country
for country, count in sorted_country_player_count:
    print(f"{country}: {count}")