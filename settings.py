APP_SIZE = (400, 700)

ORANGE_BG = "#cc7312"
GRAY = "#73696c"
CLOSE_RED = "#8a0606"
DARK_GRAY = "#3b3b3b"
APP_BACKGROUND = "#2b2b2b"
BAD_RED = "#d61c0f"
AVERAGE_ORANGE = "#e87e0c"
GOOD_GREEN = "#64e80c"
PLAYER_OFM_BLUE = "#0c9be8"

TABLE_COLOURS = ["#C0392B", "#27AE60", "#2980B9", "#8E44AD", "#D35400", "#16A085", "#F39C12", "#E74C3C", "#3498DB", "#9B59B6", "#2ECC71", "#E67E22", "#1ABC9C", "#F1C40F", "#E74C3C", "#2980B9", "#8E44AD", "#27AE60", "#C0392B", "#D35400", "#9B59B6", "#2ECC71", "#E67E22", "#16A085"]

Europe = [
    "Albania", "Andorra", "Austria", "Belgium", 
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czech Republic", "Denmark", 
    "Estonia", "Finland", "France", "Germany", "Greece", 
    "Hungary", "Iceland", "Ireland", "Italy", "Latvia", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Montenegro", 
    "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", 
    "Romania", "Serbia", "Slovakia", "Slovenia", "Spain", 
    "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom"
]

Africa = [
    "Algeria", "Cameroon", "Egypt", "Ethiopia", "Ghana", 
    "Ivory Coast", "Kenya", "Morocco", "Nigeria", "South Africa"
]

Americas = [
    "Argentina", "Brazil", "Bolivia", "Canada", "Chile", 
    "Colombia", "Ecuador", "Mexico", "Peru", "United States", 
    "Uruguay", "Venezuela"
]

Asia = [
    "China", "India", "Indonesia", "Iran", "Japan", 
    "Malaysia", "Saudi Arabia", "South Korea", "Thailand", "Vietnam",
    "Philippines"
]

continents = [Europe, Africa, Americas, Asia]
continentWeights = {"Europe": 0.7, "Africa": 0.05, "North/South America": 0.2, "Asia": 0.05}

mainCountries = ["France", "Germany", "Italy", "Netherlands", "Spain", "United Kingdom"]
westernEurope = ["Austria", "Belgium", "Denmark", "Finland", "Ireland", "Norway", "Portugal", "Sweden", "Switzerland"]
smallCountries = ["Andorra", "Luxembourg", "Malta", "Iceland"]
europeWeights = {
    country: 0.6 if country in mainCountries else (0.2 if country in westernEurope else (0.1 if country in smallCountries else 0.1))
    for country in Europe
}
africaWeights = {country: 0.1 for country in Africa}
americasWeights = {country: 0.083 for country in Americas}
asiaWeights = {country: 0.091 for country in Asia}

# Combining everything
COUNTRIES = {
    "Europe": (continentWeights["Europe"], europeWeights),
    "Africa": (continentWeights["Africa"], africaWeights),
    "North/South America": (continentWeights["North/South America"], americasWeights),
    "Asia": (continentWeights["Asia"], asiaWeights)
}

APP_FONT = "Arial"
APP_FONT_BOLD = "Arial bold"

RGBCOLORS = [
    (0, 0, 0), (30, 30, 30), (36, 36, 0), (60, 60, 60), (90, 90, 90), (120, 120, 120), (150, 150, 150),
    (180, 180, 180), (255, 255, 255), (240, 240, 240), (210, 210, 210),  (255, 240, 240), (255, 225, 225), 
    (255, 210, 210), (255, 195, 195), (255, 180, 180), (255, 165, 165), (255, 150, 150),
    (255, 135, 135), (255, 120, 120), (255, 105, 105), (255, 90, 90), (255, 75, 75), (255, 60, 60), (255, 45, 45), (255, 30, 30),
    (255, 15, 15), (255, 0, 0), (255, 36, 0), (255, 72, 0), (255, 109, 0), (255, 145, 0), (255, 182, 0), (255, 218, 0),
    (255, 255, 0), (218, 255, 0), (182, 255, 0), (145, 255, 0), (109, 255, 0), (72, 255, 0), (36, 255, 0), (0, 255, 0),
    (0, 255, 36), (0, 255, 72), (0, 255, 109), (0, 255, 145), (0, 128, 128), (0, 255, 182), (0, 255, 218), (0, 255, 255), (0, 218, 255),
    (0, 182, 255), (0, 145, 255), (0, 109, 255), (0, 72, 255), (0, 36, 255), (0, 0, 255), (36, 0, 255), (72, 0, 255),
    (109, 0, 255), (128, 0, 128), (145, 0, 255), (182, 0, 255), (218, 0, 255), (255, 0, 255), (255, 0, 218), (255, 0, 182), (255, 0, 145),
    (255, 0, 109), (255, 0, 72), (255, 0, 36), (255, 36, 36), (255, 72, 72), (255, 109, 109), (255, 145, 145), (255, 182, 182),
    (255, 218, 218), (218, 218, 255), (182, 182, 255), (145, 145, 255), (109, 109, 255), (72, 72, 255), (36, 36, 255), (36, 36, 218),
    (72, 72, 182), (109, 109, 145), (145, 145, 109), (182, 182, 72), (218, 218, 36), (218, 218, 0), (182, 182, 0), (145, 145, 0), (128, 128, 0),
    (109, 109, 0), (72, 72, 0), (36, 36, 0)
]