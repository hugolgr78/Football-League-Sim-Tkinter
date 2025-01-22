import customtkinter as ctk
from settings import *
import json, random, re, os, heapq
from PIL import Image, ImageTk
from faker import Faker

# Class that oversees the menu for a league
class LeagueMenu(ctk.CTkTabview): 
    def __init__(self, parent, mainMenu, name, divisions, numTeams, numPromotions, teamsMenu, rootWindow):
        super().__init__(parent)

        self.add("Table")
        self.add("Matches")
        self.add("Stats")
        self.add("Graphs")
        self.add("Records")
        self.add("Seasons")

        self.divisions = divisions
        self.numTeams = numTeams
        self.parent = parent
        self.teamsMenu = teamsMenu
        self.mainMenu = mainMenu
        self.name = name
        self.root = rootWindow

        self.tableMenu = TableMenu(self.tab("Table"), name, numTeams, divisions, numPromotions, mainMenu, self)
        self.matchesMenu = MatchesMenu(self.tab("Matches"), numTeams, divisions, self)
        self.statsMenu = StatsMenu(self.tab("Stats"), self, name)
        self.graphsMenu = GraphsMenu(self.tab("Graphs"), numTeams, name, self)
        self.recordsMenu = RecordsMenu(self.tab("Records"), name, self)
        self.seasonsMenu = SeasonsMenu(self.tab("Seasons"), self, name)

        self._segmented_button.grid(sticky = "w")

        self.backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBack())
        self.backButton.place(x = 378, y = 0, anchor = "ne")

        self.newSeasonButton = ctk.CTkButton(self, text = "New", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", width = 34, height = 15, corner_radius = 5, state = "disabled", command = lambda: self.newSeason())
        self.newSeasonButton.place(x = 378, y = 20, anchor = "ne")

    def goBack(self):
        self.matchesMenu.saveTable() # save the data from the table
        self.mainMenu.pack(expand = True, fill = "both")

        # if the teams havent been selected, reset. This is only ran when creating a new league
        if(hasattr(self.tableMenu, "selectedVar")):
            self.tableMenu.selectedTeams = []
            self.tableMenu.selectedVar.set(0)
            self.tableMenu.selectionFrame.place_forget()
            self.tableMenu.createTableFrame.place_forget()

        self.tableMenu.addTeamsButton.place(x = 185, y = 280, anchor = "center")

        self.pack_forget()

    def importData(self, leagueData):
        self.tableMenu.addTeamsButton.place_forget()

        # add the teams to the table along with their data
        self.tableMenu.numTeams = (len(leagueData["teams"]))
        self.tableMenu.name = leagueData["name"]
        self.tableMenu.addTeams(leagueData, True)

    def newSeason(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
            
            with open("players.json", "r") as file:
                teams = json.load(file)

            with open("teams.json", "r") as file:
                teamsBasic = json.load(file)

            with open("leagues.json") as file:
                leagues = json.load(file)
            
            with open("seasonsData.json") as file:
                seasonsData = json.load(file)
            
            with open("settings.json") as file:
                settings = json.load(file)
        except:
            leaguesData = []
            teams = []
            leagues = []
            seasonsData = []
            settings = []
        
        # get the winner of the season, which will be the first list (and then the name is first index of the list)
        winner = self.tableMenu.tableTeams[0][0]

        hattrickCounts = {}
        goalsWithoutPenaltiesCount = {}
        mostGoalsInGame = {"name": None, "goals": 0, "against": None}

        # reset the data in the json file
        for league in leaguesData:
            if league["name"] == self.name:
                currLeague = league
  
                for matchday in currLeague['matchDays']: # before resseting the matchDays, find the individual records
                    for match in matchday['matches']:
                        matchGoalCounts = {}
                        for scorer in match['homeScorers'] + match['awayScorers']:
                            if scorer['type'] in ['goal', 'penalty']:
                                # if scorer['name'] not in goalCounts:
                                #     goalCounts[scorer['name']] = 1
                                # else:
                                #     goalCounts[scorer['name']] += 1

                                # if scorer['type'] == 'penalty':
                                #     if scorer['name'] not in penaltyCounts:
                                #         penaltyCounts[scorer['name']] = 1
                                #     else:
                                #         penaltyCounts[scorer['name']] += 1

                                if scorer['type'] == 'goal':
                                    if scorer['name'] not in goalsWithoutPenaltiesCount:
                                        goalsWithoutPenaltiesCount[scorer['name']] = 1
                                    else:
                                        goalsWithoutPenaltiesCount[scorer['name']] += 1

                                if scorer['name'] not in matchGoalCounts:
                                    matchGoalCounts[scorer['name']] = 1
                                else:
                                    matchGoalCounts[scorer['name']] += 1
                            
                                # if scorer["assister"] != "none":
                                #     if scorer['assister'] not in assistsCounts:
                                #         assistsCounts[scorer['assister']] = 1
                                #     else:
                                #         assistsCounts[scorer['assister']] += 1

                        # if match["playerOTM"] not in playerOTMCounts:
                        #     playerOTMCounts[match["playerOTM"]] = 1
                        # else:
                        #     playerOTMCounts[match["playerOTM"]] += 1
                    
                        for player, goalCount in matchGoalCounts.items():
                            if goalCount >= 3:
                                if player not in hattrickCounts:
                                    hattrickCounts[player] = 1
                                else:
                                    hattrickCounts[player] += 1
                            
                            if goalCount > mostGoalsInGame["goals"]:
                                mostGoalsInGame["name"] = player
                                mostGoalsInGame["goals"] = goalCount

                                found = False
                                for scorer in match["homeScorers"]:
                                    if scorer["name"] == mostGoalsInGame["name"]:
                                        mostGoalsInGame["against"] = match["away"]
                                        found = True

                                if not found:
                                    mostGoalsInGame["against"] = match["home"]

                league["matchDays"] = [] # reset the matchdays
                seasonTopScorer = league["topScorer"][0]
                league["topScorer"] = []
                seasonTopAssister = league["topAssister"][0]
                league["topAssister"] = []
                seasonTopAverageRating = league["topAverageRating"][0]
                league["topAverageRating"] = []
                seasonTopCleanSheets = league["topCleanSheet"][0]
                league["topCleanSheet"] = []
                seasonTopPens = league["topPen"][0]
                league["topPen"] = []
                seasonTopPOTM = league["topPOTM"][0]
                league["topPOTM"] = []

                break
        
        mostTimesWon = 0
        mostTimesTeam = ""
        for team in currLeague["teams"]: # update the data for each team
            teamRecords = team["seasonRecords"]

            # update the team's records for that league
            teamRecords["won"] = int(team["w"]) + int(teamRecords["won"])
            teamRecords["drawn"] = int(team["d"]) + int(teamRecords["drawn"])
            teamRecords["lost"] = int(team["l"]) + int(teamRecords["lost"])
            teamRecords["goalsScored"] = int(team["gf"]) + int(teamRecords["goalsScored"])
            teamRecords["goalsConceded"] = int(team["ga"]) + int(teamRecords["goalsConceded"])

            # reset their data
            team["gp"] = 0
            team["w"] = 0
            team["d"] = 0
            team["l"] = 0
            team["gf"] = 0
            team["ga"] = 0
            team["gd"] = 0
            team["p"] = 0

            team["positions"] = []
            team["points"] = []

            #  update the timesWon record if they were the winner
            if team["name"] == winner.cget("text"):
                teamRecords["timesWon"] = 1 + int(teamRecords["timesWon"])

            # update the variables to find the team who won the league the most times
            if teamRecords["timesWon"] > mostTimesWon:
                mostTimesWon = teamRecords["timesWon"]
                mostTimesTeam = team["name"]

        with open("leaguesData.json", "w") as file:
            json.dump(leaguesData, file)

        if settings["levelChange"] == 1:
            # update the team's level according to their finising position and the list levels [200, 198, 196, ..., 2]
            levels = list(range(200, 1, -2))
            for index, team in enumerate(self.tableMenu.tableTeams):
                for teamData in teamsBasic:
                    if team[0].cget("text") == teamData["name"]:
                        teamData["level"] = levels[index]
            
            changedLevels = True
        else:
            changedLevels = False

        with open("teams.json", "w") as file:
            json.dump(teamsBasic, file)
        
        for team in teams:
            if team["name"] in [team[0].cget("text") for team in self.tableMenu.tableTeams]:
                winTeam = True if team["name"] == winner.cget("text") else False

                for player in team["players"]:

                    if winTeam:
                        if self.name in list(player["trophies"].keys()):
                            player["trophies"][self.name] += 1
                        else:
                            player["trophies"][self.name] = 1

                    for ban in player["matchBan"]:
                        if ban["compName"] == self.name:
                            ban["ban"] = 0
                            ban["type"] = "none"
                            
                    for data in player["seasonStats"]:
                        if data["compName"] == self.name:

                            playerSeasonsData = player["seasonsData"]

                            for league in leagues:
                                if league["name"] == self.name:
                                    season = league["seasons"]
                            
                            newEntry = {
                                "season": season,
                                "goals": data["goals"],
                                "assists": data["assists"],
                                "reds": data["reds"],
                                "clean sheets": data["clean sheets"],
                                "averageRating": data["averageRating"],
                                "played": data["played"]
                            }

                            for season in playerSeasonsData:
                                if season["compName"] == self.name:
                                    season["seasons"].append(newEntry)
                        
                            data["goals"] = 0
                            data["assists"] = 0
                            data["reds"] = 0
                            data["clean sheets"] = 0
                            data["averageRating"] = 0.00
                            data["played"] = 0
                            data["pens"] = 0
                            data["MOTM"] = 0
                    
                    player["matches"] = [match for match in player["matches"] if match["compName"] != self.name]

        with open("players.json", "w") as file:
            json.dump(teams, file)

        for league in leagues: # update the leagues data in leagues.json
            if league["name"] == self.name:

                teamRecords = league["teamRecords"]
                individualRecords = league["individualRecords"]
                currSeason = league["seasons"]
        
                valuesIndex = 2
                recordsIndex = 0
                recordsTitles = ["most wins", "least wins", "most draws", "least draws", "most losses", "least losses", "most goals scored", "least goals scored", "most goals conceded", "least goals conceded", "most goal difference", "least goal difference", "most points", "least points"]
                for i in range(7): # this loop will first get the most, then least of whatever record it is currently on, then go onto the next and update accordingly
                    value, team = self.getData(valuesIndex)
                    if value > teamRecords[recordsTitles[recordsIndex]]["value"] or teamRecords[recordsTitles[recordsIndex]]["value"] == 1000: # value starts at 1000, otherwise "least" records wont be added if the value is 0
                        teamRecords[recordsTitles[recordsIndex]]["value"] = value
                        teamRecords[recordsTitles[recordsIndex]]["team"] = team
                        teamRecords[recordsTitles[recordsIndex]]["season"] = league["seasons"]

                    value, team = self.getData(valuesIndex, False)
                    if value < teamRecords[recordsTitles[recordsIndex + 1]]["value"] or teamRecords[recordsTitles[recordsIndex]]["value"] == 1000:
                        teamRecords[recordsTitles[recordsIndex + 1]]["value"] = value
                        teamRecords[recordsTitles[recordsIndex + 1]]["team"] = team
                        teamRecords[recordsTitles[recordsIndex + 1]]["season"] = league["seasons"]

                    valuesIndex += 1
                    recordsIndex += 2

                # recordsTitles = ["most goals", "most hattricks", "most penalties", "most goals without penalties", "most goals in one game", "most assists", "most player of the match awards"]
                # lists = [goalCounts, hattrickCounts, penaltyCounts, goalsWithoutPenaltiesCount, mostGoalsInGame, assistsCounts, playerOTMCounts]
                recordsTitles = ["most hattricks", "most goals without penalties", "most goals in one game"]
                lists = [hattrickCounts, goalsWithoutPenaltiesCount, mostGoalsInGame]

                for i in range(len(recordsTitles)): # update individual records
                    if lists[i] != {}:
                        if i != 2:
                            recordPlayer = max(lists[i], key = lists[i].get)
                            value = lists[i][recordPlayer]
                        else:
                            recordPlayer = mostGoalsInGame["name"]
                            value = mostGoalsInGame["goals"]
                            against = mostGoalsInGame["against"]

                        if value > individualRecords[recordsTitles[i]]["value"] or individualRecords[recordsTitles[i]]["value"] == 1000:
                            individualRecords[recordsTitles[i]]["player"] = recordPlayer
                            individualRecords[recordsTitles[i]]["value"] = value

                            if i == 2:
                                individualRecords[recordsTitles[i]]["against"] = against

                            try:
                                with open("players.json", "r") as file:
                                    teams = json.load(file)
                            except:
                                teams = []
                        
                            for team in teams:
                                for player in team["players"]:
                                    if player["name"] == recordPlayer:
                                        individualRecords[recordsTitles[i]]["team"] = team["name"]
                                        break

                            individualRecords[recordsTitles[i]]["season"] = league["seasons"]

                recordsTitles = ["most goals", "most assists", "best average rating", "most clean sheets", "most penalties", "most player of the match awards"]
                lists = [seasonTopScorer, seasonTopAssister, seasonTopAverageRating, seasonTopCleanSheets, seasonTopPens, seasonTopPOTM]

                for i in range(len(recordsTitles)):
                    if (lists[i]["stat"] > individualRecords[recordsTitles[i]]["value"] or individualRecords[recordsTitles[i]]["value"] == 1000) and lists[i]["stat"] != 0:
                        individualRecords[recordsTitles[i]]["player"] = lists[i]["name"]
                        individualRecords[recordsTitles[i]]["value"] = lists[i]["stat"]
                        individualRecords[recordsTitles[i]]["team"] = lists[i]["team"]
                        individualRecords[recordsTitles[i]]["season"] = league["seasons"]

                league["seasons"] = league["seasons"] + 1 # update the number of seasons the league has had

                # update the final record
                teamRecords["most times won"]["value"] = mostTimesWon
                teamRecords["most times won"]["team"] = mostTimesTeam

        with open("leagues.json", "w") as file:
            json.dump(leagues, file)

        ## save the table data and winner to the seasonsData file
        for league in seasonsData:
            if league["name"] == self.name:

                league["winners"].append(winner.cget("text"))

                newEntry = {
                    "season": currSeason,
                    "table": []
                }

                positionsEntry = {
                    "season": currSeason,
                    "positions": self.matchesMenu.positions
                }

                pointsEntry = {
                    "season": currSeason,
                    "points": self.matchesMenu.points
                }

                topScorersEntry = {
                    "season": currSeason,
                    "topScorer": seasonTopScorer
                }

                topAssistersEntry = {
                    "season": currSeason,
                    "topAssister": seasonTopAssister
                }

                topAverageRatingEntry = {
                    "season": currSeason,
                    "topAverageRating": seasonTopAverageRating
                }

                topCleanSheetsEntry = {
                    "season": currSeason,
                    "topCleanSheet": seasonTopCleanSheets
                }

                topPensEntry = {
                    "season": currSeason,
                    "topPen": seasonTopPens
                }

                topPOTMEntry = {
                    "season": currSeason,
                    "topPOTM": seasonTopPOTM
                }

                for team in self.tableMenu.tableTeams:
                    entry =  {
                        "team": team[0].cget("text"),
                        "gp": team[1].cget("text"),
                        "w": team[2].cget("text"),
                        "d": team[3].cget("text"),
                        "l": team[4].cget("text"),
                        "gf": team[5].cget("text"),
                        "ga": team[6].cget("text"),
                        "gd": team[7].cget("text"),
                        "p": team[8].cget("text")
                    }
                    newEntry["table"].append(entry)
                
                league["tables"].append(newEntry)
                league["positions"].append(positionsEntry)
                league["points"].append(pointsEntry)
                league["topScorer"].append(topScorersEntry)
                league["topAssister"].append(topAssistersEntry)
                league["topAverageRating"].append(topAverageRatingEntry)
                league["topCleanSheet"].append(topCleanSheetsEntry)
                league["topPen"].append(topPensEntry)
                league["topPOTM"].append(topPOTMEntry)

        with open("seasonsData.json", "w") as file:
            json.dump(seasonsData, file)
        
        # this will reset the table values to 0. isNeg is needed for goal difference
        for teamLabels in self.tableMenu.tableTeams:
            for label in teamLabels:
                if label.cget("text").isdigit() or self.isNeg(label.cget("text")):
                    label.configure(text = "0")

        positionsCopy = self.matchesMenu.positions
        pointsCopy = self.matchesMenu.points

        for team in positionsCopy:
            positionsCopy[team] = []
            pointsCopy[team] = []

        self.newSeasonButton.configure(state = "disabled")
        self.matchesMenu.destroy() # destroy the matches menu
        self.matchesMenu = MatchesMenu(self.tab("Matches"), self.numTeams, self.divisions, self) # create a new matches menu
        self.matchesMenu.sortTable(False) # sort the table alphabetically
        self.matchesMenu.positions = positionsCopy
        self.matchesMenu.points = pointsCopy

        self.graphsMenu.destroy()
        self.graphsMenu = GraphsMenu(self.tab("Graphs"), self.numTeams, self.name, self)
        self.graphsMenu.addGraph(True)

        self.seasonsMenu.pack_forget()
        self.seasonsMenu = SeasonsMenu(self.tab("Seasons"), self, self.name)
        self.seasonsMenu.importSeasons()

        self.statsMenu.destroy()
        self.statsMenu = StatsMenu(self.tab("Stats"), self, self.name)
        self.statsMenu.importStats()

        if changedLevels:   
            self.teamsMenu.updateLevels() # call the updateLevels function in menu.py which will change the level labels in the teams menu

        self.recordsMenu.addTeamRecords(True) # update the league's records (True says that they are replacing old ones)
        self.recordsMenu.addIndividualRecords(True)

    def getData(self, index, most = True):
        data = self.tableMenu.tableTeams

        value = None
        team = ""
        for labels in data:
            if value is None: # get a starting value
                    value = int(labels[index].cget("text"))
                    team = labels[0].cget("text")
            elif most: # if most is True, get the most value
                if int(labels[index].cget("text")) > value:
                    value = int(labels[index].cget("text"))
                    team = labels[0].cget("text")
            else: # if not, get the least value
                if int(labels[index].cget("text")) <= value:
                    value = int(labels[index].cget("text"))
                    team = labels[0].cget("text")

        return value, team

    def isNeg(self, str):
        # this function will return wether a string is negative number or not
        if str.startswith('-') and str[1:].isdigit():
            return True
        return False

# Class that oversees the table of the league
class TableMenu(ctk.CTkFrame):
    def __init__(self, parent, name, numTeams, divisions, numPromotions, mainMenu, leagueMenu):
        super().__init__(parent)
        self.pack(expand = True, fill = "both") 
        self.name = name
        self.parent = leagueMenu
        self.name = name
        self.numTeams = numTeams
        self.divisons = divisions
        self.numPromotions = numPromotions
        self.mainMenu = mainMenu

        self.addTeamsButton = ctk.CTkButton(self, text = "Add teams", fg_color = ORANGE_BG, command = lambda: self.selectTeams())
        self.addTeamsButton.place(x = 185, y = 280, anchor = "center")

        self.selectedTeams = [] # this list will contain the teams the user selects to be in the league
        self.tableTeams = []

    def selectTeams(self):

        # read teams from json file
        try:
            with open("teams.json", "r") as file:
                self.teams = json.load(file)
        except:
            self.teams = []

        self.selectedVar = ctk.IntVar(value = 0) # length of selectedTeams at any time

        self.addTeamsButton.place_forget()

        self.selectionFrame = ctk.CTkScrollableFrame(self, fg_color = ORANGE_BG, width = 200, height = 400)
        self.selectionFrame.place(x = 185, y = 280, anchor = "center")

        self.createTableFrame = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 223, height = 60)
        self.createTableFrame.place(x = 185, y = 520, anchor = "center")

        self.selectionFrame.grid_columnconfigure(0, weight = 2, uniform = "a")
        self.selectionFrame.grid_columnconfigure(1, weight = 7, uniform = "a")
        self.selectionFrame.grid_columnconfigure(2, weight = 3, uniform = "a")

        for i in range(self.numTeams):
            self.selectionFrame.grid_rowconfigure(i + 3, weight = 1)

        self.searchFrame = ctk.CTkFrame(self.selectionFrame, fg_color = ORANGE_BG, width = 223, height = 30)
        self.searchFrame.grid(row = 1, column = 0, columnspan = 3, padx = 5)
        self.searchFrame.grid_columnconfigure(0, weight = 2)
        self.searchFrame.grid_columnconfigure(1, weight = 1)
        self.searchFrame.grid_columnconfigure(2, weight = 1)
        self.searchFrame.grid_rowconfigure(0, weight = 1)
        self.searchFrame.grid_propagate(False)

        self.searchVar = ctk.StringVar()
        self.searchEntry = ctk.CTkEntry(self.searchFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 250, textvariable = self.searchVar)
        self.searchEntry.grid(row = 0, column = 0, padx = 5)

        self.searchButton = ctk.CTkButton(self.searchFrame, text = "Search", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, command = lambda: self.searchTeams(self.searchVar.get()))
        self.searchButton.grid(row = 0, column = 1, padx = 5)

        self.resetButton = ctk.CTkButton(self.searchFrame, text = "Reset", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, state = "disabled", command = lambda: self.reset())
        self.resetButton.grid(row = 0, column = 2, padx = 5)        

        checkFrame = ctk.CTkFrame(self.selectionFrame, fg_color = ORANGE_BG)
        checkFrame.grid(row = 2, column = 0, columnspan = 3, pady = 5)
        checkFrame.grid_columnconfigure((0, 1), weight = 1)
        
        src = Image.open("Images/checked.png")
        img = ctk.CTkImage(src, None, (20, 20))
        checkAllButton = ctk.CTkButton(checkFrame, text = "", image = img, fg_color = ORANGE_BG, hover_color = ORANGE_BG, corner_radius = 5, width = 1, command = lambda: self.checkAllBoxes(True))
        checkAllButton.grid(row = 0, column = 0, padx = (5, 15))

        src = Image.open("Images/unchecked.png")
        img = ctk.CTkImage(src, None, (20, 20))
        checkNoneButton = ctk.CTkButton(checkFrame, text = "", image = img, fg_color = ORANGE_BG, hover_color = ORANGE_BG, corner_radius = 5, width = 1, command = lambda: self.checkAllBoxes(False))
        checkNoneButton.grid(row = 0, column = 1, padx = (15, 5))

        self.checkBoxes = []

        if(len(self.teams) < self.numTeams): # if there are not enough teams, display a message
            ctk.CTkLabel(self.selectionFrame, text = "Not enough teams\n have been created for\n a league of " + str(self.numTeams) + " teams", fg_color = ORANGE_BG, text_color = "white", font = (APP_FONT_BOLD, 15)).grid(row = 10, column = 0, columnspan = 3)
        else:
            for i in range(len(self.teams)):
                # add the name, logo and a checkbox for each team in the players.json file
                src = Image.open(self.teams[i]["logoPath"])
                logo = ctk.CTkImage(src, None, (20, 20))
                ctk.CTkLabel(self.selectionFrame, text = "", image = logo, fg_color = ORANGE_BG).grid(row = i + 3, column = 0)
    
                ctk.CTkLabel(self.selectionFrame, text = self.teams[i]["name"], fg_color = ORANGE_BG, text_color = "black", font = (APP_FONT_BOLD, self.getFont(self.teams[i]["name"]))).grid(row = i + 3, column = 1, padx = 10)
                checkBox = ctk.CTkCheckBox(self.selectionFrame, text = "", fg_color = ORANGE_BG, command = lambda n = i: self.checkboxClicked(self.teams[n]))
                checkBox.grid(row = i + 3, column = 2, padx = 10)
                self.checkBoxes.append(checkBox)

            self.selectButton = ctk.CTkButton(self.createTableFrame, text = "Create Table", fg_color = GRAY, state = "disabled", command = lambda: self.addTeams(self.selectedTeams))
            self.selectButton.place(x = 107, y = 40, anchor = "center")

            self.selectedLabel = ctk.CTkLabel(self.createTableFrame, text = "Selected: " + str(self.selectedVar.get()) + " teams", fg_color = ORANGE_BG, font = (APP_FONT_BOLD, 15))
            self.selectedLabel.place(x = 107, y = 10, anchor = "center")
    
    def addTeams(self, listData, importData = False):
        self.listData = listData

        if not importData: # if not imported, remove the frames
            self.selectionFrame.place_forget()
            self.createTableFrame.place_forget()

        tableFrame = ctk.CTkFrame(self, fg_color = GRAY)
        tableFrame.pack(expand = True, fill = "both")
        tableFrame.grid_propagate(False)

        tableFrame.grid_columnconfigure(0, weight = 3)
        tableFrame.grid_columnconfigure(1, weight = 6)
        tableFrame.grid_columnconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight = 1)
        tableFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)

        self.tableTeams = [] # this list is important, it holds lists of labels for each team, which will be configured to update table, and read from to save the table data
        self.tableLogos = [] # this list holds the logos of each team, necessary for sorting the table
        ctk.CTkLabel(tableFrame, text = "#", fg_color = GRAY, text_color = "black").grid(row = 0, column = 0)
        ctk.CTkLabel(tableFrame, text = "Team", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 2, sticky = "w")
        ctk.CTkLabel(tableFrame, text = "GP", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 3)
        ctk.CTkLabel(tableFrame, text = "W", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 4)
        ctk.CTkLabel(tableFrame, text = "D", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 5)
        ctk.CTkLabel(tableFrame, text = "L", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 6)
        ctk.CTkLabel(tableFrame, text = "GF", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 7)
        ctk.CTkLabel(tableFrame, text = "GA", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 8)
        ctk.CTkLabel(tableFrame, text = "GD", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 9)
        ctk.CTkLabel(tableFrame, text = "P", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 10)

        if not importData: # whether imported or not, the list data will be different (not imported it is self.selectedTeams)
            self.listData.sort(key = lambda x: x["name"]) # sort the list of teams by name

            for i in range(self.numTeams):
                teamLabels = []
                ctk.CTkLabel(tableFrame, text = i + 1, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).grid(row = i + 1, column = 0) # position

                src = Image.open(self.listData[i]["logoPath"])
                logo = ctk.CTkImage(src, None, (20, 20))
                logoLabel = ctk.CTkLabel(tableFrame, text = "", image = logo, fg_color = GRAY)
                logoLabel.grid(row = i + 1, column = 1)
                self.tableLogos.append(logoLabel)

                nameLabel = ctk.CTkLabel(tableFrame, text = self.listData[i]["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 12))
                nameLabel.grid(row = i + 1, column = 2, sticky = "w")
                teamLabels.append(nameLabel)

                for j in range(8): # values for gp, w, d, l, etc...
                    label = ctk.CTkLabel(tableFrame, text = "0", fg_color = GRAY, text_color = "black", font = (APP_FONT, 15))
                    label.grid(row = i + 1, column = j + 3)

                    teamLabels.append(label)

                self.tableTeams.append(teamLabels)
                self.parent.matchesMenu.positions[self.listData[i]["name"]] = []
                self.parent.matchesMenu.points[self.listData[i]["name"]] = []

            self.saveData() # save the data to the json file
            self.parent.matchesMenu.importBans()

        else: # when imported, listsData is the data in leaguesData.json file
            dictEntries = ["gp", "w", "d", "l", "gf", "ga", "gd", "p"] # used to get the values from the json file
            for i in range(self.numTeams):
                teamLabels = []
                ctk.CTkLabel(tableFrame, text = i + 1, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).grid(row = i + 1, column = 0) # position

                src = Image.open(self.listData["teams"][i]["logoPath"])
                logo = ctk.CTkImage(src, None, (20, 20))
                logoLabel = ctk.CTkLabel(tableFrame, text = "", image = logo, fg_color = GRAY)
                logoLabel.grid(row = i + 1, column = 1)
                self.tableLogos.append(logoLabel)

                nameLabel = ctk.CTkLabel(tableFrame, text = self.listData["teams"][i]["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 12))
                nameLabel.grid(row = i + 1, column = 2, sticky = "w")
                teamLabels.append(nameLabel)

                for j in range(8):
                    label = ctk.CTkLabel(tableFrame, text = self.listData["teams"][i][dictEntries[j]], fg_color = GRAY, text_color = "black", font = (APP_FONT, 15))
                    label.grid(row = i + 1, column = j + 3)

                    teamLabels.append(label)

                self.parent.matchesMenu.positions[self.listData["teams"][i]["name"]] = self.listData["teams"][i]["positions"]
                self.parent.matchesMenu.points[self.listData["teams"][i]["name"]] = self.listData["teams"][i]["points"]
                    
                self.tableTeams.append(teamLabels)

            self.parent.matchesMenu.sortTable() # sort the table by points. If everything is 0, it will be sorted alphabetically
        
    def saveData(self):
        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)

            with open("players.json", "r") as file:
                teamsData = json.load(file)

            with open("teams.json", "r") as file:
                teamsBasic = json.load(file)
        except:
            data = []
            teamsData = []
            teamsBasic = []

        for league in data:
            if league['name'] == self.name:
                teams = league["teams"]

        # add every team to the league data in leaguesData.json. The data is the data stored in self.tableTeams, as mentioned above
        for team in self.tableTeams:
            team = {
                "name": team[0].cget("text"),
                "logoPath": "SavedImages/Teams/" + team[0].cget("text") + ".png",
                "gp": team[1].cget("text"),
                "w": team[2].cget("text"),
                "d": team[3].cget("text"),
                "l": team[4].cget("text"),
                "gf": team[5].cget("text"),
                "ga": team[6].cget("text"),
                "gd": team[7].cget("text"),
                "p": team[8].cget("text"),
                "positions": [],
                "points": [],
                "seasonRecords": {
                    "won": 0,
                    "drawn": 0, 
                    "lost": 0,
                    "goalsScored": 0,
                    "goalsConceded": 0,
                    "timesWon": 0
                }
            }

            teams.append(team)
        
        # add the league name to every team in the league
        for team in teamsBasic:
            if(team["name"] in [team[0].cget("text") for team in self.tableTeams]):
                team["competitions"].append(self.name)

        for team in teamsData:
            if(team["name"] in [team[0].cget("text") for team in self.tableTeams]):
                for player in team["players"]:
                    compEntry = {
                        "compName": self.name,
                        "goals": 0,
                        "assists": 0,
                        "reds": 0,
                        "clean sheets": 0,
                        "averageRating": 0.00,
                        "pens": 0,
                        "MOTM": 0,
                        "played": 0
                    }
                
                    player["seasonStats"].append(compEntry)

                    seasonEntry = {
                        "compName": self.name,
                        "seasons": []
                    }

                    player["seasonsData"].append(seasonEntry)

                    banEntry = {
                        "compName": self.name,
                        "ban": 0,
                        "banType": "none",
                        "type": "none"
                    }

                    player["matchBan"].append(banEntry)

        with open("leaguesData.json", "w") as file:
            json.dump(data, file, indent = 4)

        with open("players.json", "w") as file:
            json.dump(teamsData, file, indent = 4)
        
        with open("teams.json", "w") as file:
            json.dump(teamsBasic, file, indent = 4)

    def checkboxClicked(self, team):
        # this function is called whenever a checkbox is clicked. It will add / remove the team from self.selectedTeams and increase / decrease self.selectedVar
        if team in self.selectedTeams:
            self.selectedTeams.remove(team)
            self.selectedVar.set(self.selectedVar.get() - 1)
        else:
            self.selectedTeams.append(team)
            self.selectedVar.set(self.selectedVar.get() + 1)

        # update the selected label
        self.selectedLabel.configure(text = "Selected: " + str(self.selectedVar.get()) + " teams")

        # enable the select button if the number of selected teams is equal to the number of teams in the league
        if (self.selectedVar.get() == self.numTeams):
            self.selectButton.configure(state = "normal")
        else:
            self.selectButton.configure(state = "disabled")

    def checkAllBoxes(self, check):
        for i in range(len(self.teams)):
            if check and self.checkBoxes[i].get() == 0:
                self.checkBoxes[i].select()
                self.checkboxClicked(self.teams[i])
            elif not check and self.checkBoxes[i].get() == 1:
                self.checkBoxes[i].deselect()
                self.checkboxClicked(self.teams[i])

    def getFont(self, string):
        if (len(string) <= 10):
            return 15
        if (len(string) < 15):
            return 12
        if (len(string) >= 15):
            return 8

# Class that oversees the matchdays of the league
class MatchesMenu(ctk.CTkFrame):    
    def __init__(self, parent, numTeams, divisions, leagueMenu):
        super().__init__(parent)
        self.pack(expand = True, fill = "both") 
        self.schedule = [] # stores a list for each matchday with the games
        self.scores = [] # stores a list for each matchday with the scores
        self.activeFrame = 0 # stores the index of the active matchday frame in self.matchesFrames
        self.activeSim = [0] * ((numTeams * 2) - 2) # stores 1 for the next matchday to be simulated, 0 otherwise
        self.scoreLabels = [] # stores labels that are configured later to change the score from the time to the actual score
        self.matchesInfo = [] # stores the info of each match per matchDay
        self.lineups = [] # stores the lineups of each matchc per matchDay
        self.referees = [] # stores the referees of each match per matchDay
        self.injuries = [] # stores the injuries of each match per matchDay
        self.positions = {}  # stores the past positions of each team alphabetically
        self.points = {} # stores the points per matchday of each team
        self.banned = [] # holds the players that are banned
        self.ratings = [] # holds the ratings of each player per matchday
        self.playersData = [] # holds the player data for each match they play in
        self.playersOTM = []
        self.parent = leagueMenu
        self.numTeams = numTeams
        self.divisions = divisions

        self.topScorer = []
        self.topAssister = []
        self.topAverageRating = []
        self.topCleanSheet = []
        self.topPen = []
        self.topPOTM = []

        self.createMatchesButton = ctk.CTkButton(self, text = "Create Matches", fg_color = ORANGE_BG, command = lambda: self.createMatches())
        self.createMatchesButton.place(x = 185, y = 280, anchor = "center")

        self.matchesFrames = []

    def importMatches(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
            
            with open("players.json", "r") as file:
                playersData = json.load(file)
        except:
            leaguesData = []
            playersData = []

        self.importBans()
        
        foundMatches = False
        I = 0
        for index, league in enumerate(leaguesData): # find the league in leaguesData.json and check if it has matchdays
            if "divisions" not in league:
                if league["name"] == self.parent.tableMenu.name:
                    I = index
                    if league["matchDays"] != []:
                        foundMatches = True
                    else:
                        foundMatches = False

                    break
        
        for team in leaguesData[I]["teams"]:
            entry = {
                    "name": team["name"],
                    "players": []
                }
            
            for teamPlayers in playersData:
                if teamPlayers["name"] == team["name"]:
                    for player in teamPlayers["players"]:
                        entry["players"].append(player)

            self.playersData.append(entry)

        self.topScorer = leaguesData[I]["topScorer"]
        self.topAssister = leaguesData[I]["topAssister"]
        self.topAverageRating = leaguesData[I]["topAverageRating"]
        self.topCleanSheet = leaguesData[I]["topCleanSheet"]
        self.topPen = leaguesData[I]["topPen"]
        self.topPOTM = leaguesData[I]["topPOTM"]

        if not foundMatches: # if the league has no matchdays, return and set the first matchday as 1
            self.activeSim[0] = 1
            return
        else: # otherwise, want to add the matchdays and their scores
            self.createMatchesButton.place_forget() # remove the button
            self.numTeams = len(leaguesData[I]["teams"])
            self.createFrames() # create the frames

            # this loop will find the first matchday that hasnt been played (the first matchday to be simulated) and set it as the active matchday
            breakLoop = False
            for index, matchDay in enumerate(leaguesData[I]["matchDays"]):
                for match in matchDay["matches"]:
                    if match["played"] == 0:
                        self.activeSim[index] = 1
                        breakLoop = True
                        break
                if breakLoop:
                    break

            if self.activeSim[0] != 1:
                self.matchesFrames[0].matchDayLabel.place_forget()
                self.matchesFrames[0].matchDayLabel.place(relx = 0.69, rely = 0.5, anchor = "center")
                self.matchesFrames[0].currentMatchDayButton.place(relx = 0.3, rely = 0.5, anchor = "center")

            # loop through the frames and the matchDays
            for frame, matchDay in zip(self.matchesFrames, leaguesData[I]["matchDays"]):
                games = [] # this list will store the games for each matchday, needed to "recreate" the schedule manually
                labels = []
                matchDayInfo = []
                matchDayLineups = []
                matchDayReferees = []
                matchDayInjuries = []
                matchDayRatings = []
                matchDayPlayersOTM = []

                yPlaces = [60 + 50 * i for i in range(12)]
                for index, match in enumerate(matchDay["matches"]): # loop through every game per matchday
                    match_ = [0, 0]

                    # get the data
                    homeTeam = match["home"]
                    awayTeam = match["away"]
                    score = match["score"]
                    referee = match["referee"]
                    matchLineups = [[player["name"] for player in match["homeLineup"]], [player["name"] for player in match["awayLineup"]]]
                    matchRatings = [[player["rating"] for player in match["homeLineup"]], [player["rating"] for player in match["awayLineup"]]]
                    time = match["time"]
                    referee = match["referee"]
                    matchInfo = [match["homeScorers"], match["awayScorers"]]
                    injury = match["injured"]
                    playerOTM = match["playerOTM"]

                    if match["played"] == 1:
                        add = True
                        matchDayInfo.append(matchInfo)
                        matchDayLineups.append(matchLineups)
                        matchDayReferees.append(referee)
                        matchDayInjuries.append(injury)
                        matchDayRatings.append(matchRatings)
                        matchDayPlayersOTM.append(playerOTM)
                    else:
                        add = False

                    imglabels = {"home": "none", "away": "none"}
                    injTeam = "none"
                    redTeam = "none"

                    if injury != "none":
                        if injury in [player["name"] for player in match["homeLineup"]]:
                            injTeam = "home"
                        elif injury in [player["name"] for player in match["awayLineup"]]:
                            injTeam = "away"

                    found = False
                    for scorer in match["homeScorers"]:
                        if scorer["type"] == "red card":
                            redTeam = "home"
                            found = True
                            break

                    if not found:
                        for scorer in match["awayScorers"]:
                            if scorer["type"] == "red card":
                                redTeam = "away"
                                break

                    for team in ["home", "away"]:
                        if redTeam == team and injTeam == team:
                            imglabels[team] = "both"
                        elif redTeam == team:
                            imglabels[team] = "red"
                        elif injTeam == team:
                            imglabels[team] = "inj"

                    homeLabels = imglabels["home"]
                    awayLabels = imglabels["away"]

                    srcHome = Image.open("SavedImages/Teams/" + homeTeam + ".png")
                    logoHome = ctk.CTkImage(srcHome, None, (30, 30))

                    srcAway = Image.open("SavedImages/Teams/" + awayTeam + ".png")
                    logoAway = ctk.CTkImage(srcAway, None, (30, 30))

                    yPlaces = [60 + 50 * i for i in range(12)]
                    xPlaces = [105, 145, 180, 215, 255]

                    # add the data
                    ctk.CTkLabel(frame, text = homeTeam, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(homeTeam) > 15 else 12)).place(x = xPlaces[0], y = yPlaces[index], anchor = "ne")
                    ctk.CTkLabel(frame, text = "", image = logoHome, fg_color = GRAY).place(x = xPlaces[1], y = yPlaces[index], anchor = "ne")

                    try:
                        with open("teams.json", "r") as file:
                            teams = json.load(file)
                    except:
                        teams = []

                    for team in teams:
                        if team["name"] == homeTeam:
                            home = team
                        
                        if team["name"] == awayTeam:
                            away = team

                    if self.checkScore(score):
                        scoreLabel = ctk.CTkLabel(frame, text = "[ " + score + " ]", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))

                        scoreLabel.bind("<Enter> <Button-1>", lambda event, scoreLabel = scoreLabel, time = time, home = home, away = away, matchInfo = matchInfo, matchLineups = matchLineups, matchRatings = matchRatings, referee = referee, injury = injury, playerOTM = playerOTM: self.openMatch(scoreLabel, time, home, away, matchInfo, matchLineups, matchRatings, referee, injury, playerOTM, True))
                    else:
                        scoreLabel = ctk.CTkLabel(frame, text = score, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))
                    scoreLabel.place(x = xPlaces[2], y = yPlaces[index] + 15, anchor = "center")

                    # yPlaces = [60 + 50 * i for i in range(12)]
                    redSrc = Image.open("Images/redCard.png")
                    redCard = ctk.CTkImage(redSrc, None, (10, 10))
                    injSrc = Image.open("Images/injury.png")
                    inj = ctk.CTkImage(injSrc, None, (10, 10))

                    if homeLabels != "none":
                        if homeLabels == "red":
                            ctk.CTkLabel(frame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                        elif homeLabels == "inj":
                            ctk.CTkLabel(frame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                        else:
                            ctk.CTkLabel(frame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                            ctk.CTkLabel(frame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 165, y = yPlaces[index] - 5, anchor = "nw")

                    if awayLabels != "none":
                        if awayLabels == "red":
                            ctk.CTkLabel(frame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                        elif awayLabels == "inj":
                            ctk.CTkLabel(frame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                        else:
                            ctk.CTkLabel(frame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                            ctk.CTkLabel(frame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 185, y = yPlaces[index] - 5, anchor = "nw")

                    ctk.CTkLabel(frame, text = "", image = logoAway, fg_color = GRAY).place(x = xPlaces[3], y = yPlaces[index], anchor = "nw")
                    ctk.CTkLabel(frame, text = awayTeam, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(awayTeam) > 15 else 12)).place(x = xPlaces[4], y = yPlaces[index], anchor = "nw")
                    labels.append(scoreLabel)

                    match_[0] = homeTeam
                    match_[1] = awayTeam
                    games.append(match_)

                if add == True:
                    self.injuries.append(matchDayInjuries)
                    self.referees.append(matchDayReferees)
                    self.lineups.append(matchDayLineups)
                    self.matchesInfo.append(matchDayInfo)
                    self.ratings.append(matchRatings)
                    self.playersOTM.append(matchDayPlayersOTM)

                self.scoreLabels.append(labels)
                self.schedule.append(games) # as previously mentioned, add the games to the schedule to "recreate" it

            self.matchesFrames[0].place(x = 0, y = 0, anchor = "nw") # place the first frame
            self.actionButtonsFrame.place(x = 0, y = 585, anchor = "nw")
    
    def importBans(self):
        self.banned = []

        try:
            with open("players.json", "r") as file:
                players = json.load(file)
        except:
            players = []

        for team in players:
            if team["name"] in [team[0].cget("text") for team in self.parent.tableMenu.tableTeams]:
                for player in team["players"]:
                    for ban in player["matchBan"]:
                        if ban["banType"] == "injury":
                            add = True
                        elif ban["banType"] == "red":
                            if ban["compName"] == self.parent.name:
                                add = True
                            else:
                                add = False
                        elif ban["banType"] == "none":
                            add = False

                        if add:
                            newBan = {
                                "name": player["name"],
                                "ban": ban["ban"],
                                "type": ban["banType"],
                                "compName": ban["compName"]
                            }
                        
                            self.banned.append(newBan)
                            
    def checkScore(self, str):
        return bool(re.match(r'^\d+ : \d+$', str))
    
    def createFrames(self):
        self.createMatchesButton.place_forget() # remove the create matches button

        for i in range((self.numTeams * 2) - 2): # create a frame for each matchday, (numTeams * 2) - 2 is the number of matchdays in a league
            frame = ctk.CTkFrame(self, fg_color = GRAY, height = 580, width = 365)

            packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 25, width = 365)
            frame.matchDayLabel = ctk.CTkLabel(packFrame, text = "Matchday " + str(i + 1), fg_color = GRAY, font = (APP_FONT_BOLD, 15))
            frame.matchDayLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
            packFrame.place(x = 5, y = 5, anchor = "nw")

            frame.currentMatchDayButton = ctk.CTkButton(packFrame, text = "Current Matchday", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = self.currentMatchDay) # button to go back to the current matchday

            # ctk.CTkLabel(frame, text = "Matchday " + str(i + 1), fg_color = GRAY, font = (APP_FONT_BOLD, 15)).place(x = 180, y = 20, anchor = "center")
            self.matchesFrames.append(frame) # add the frame to the list


        self.actionButtonsFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 40, width = 365)

        self.leftArrow = ctk.CTkButton(self.actionButtonsFrame, text = "<", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(-1)) # go back a matchday
        self.leftArrow.place(x = 60, rely = 0.5, anchor = "center")

        self.rightArrow = ctk.CTkButton(self.actionButtonsFrame, text = ">", fg_color = ORANGE_BG, width = 50, bg_color = GRAY, height = 15, command = lambda: self.changeFrame(1)) # go forward a matchday
        self.rightArrow.place(x = 310, rely = 0.5, anchor = "center")

        self.simulateButton = ctk.CTkButton(self.actionButtonsFrame, text = "Simulate", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.simMatchDay()) # simulate the matchday
        self.simulateButton.place(x = 230, rely = 0.5, anchor = "center")

        self.autoButton = ctk.CTkButton(self.actionButtonsFrame, text = "Auto", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.automateMatches()) # simulate all matchdays
        self.autoButton.place(x = 140, rely = 0.5, anchor = "center")

        self.pauseButton = ctk.CTkButton(self.actionButtonsFrame, text = "Pause", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.pauseSim()) # pause the simulation, not placed as it replaces the auto button once the simulation is running

        # self.currentMatchDayButton = ctk.CTkButton(self, text = "Current\nMatchday", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = self.currentMatchDay) # button to go back to the current matchday
        
    def currentMatchDay(self):
        index = 0
        for i, frame in enumerate(self.activeSim):
            if frame == 1:
                index = i
                break
        
        self.matchesFrames[self.activeFrame].place_forget()
        self.matchesFrames[index].place(x = 0, y = 0, anchor = "nw")
        self.activeFrame = index
        self.matchesFrames[self.activeFrame].currentMatchDayButton.place_forget()
        self.matchesFrames[self.activeFrame].matchDayLabel.place_forget()
        self.matchesFrames[self.activeFrame].matchDayLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

    def changeFrame(self, direction):
        # this function is used to change which frame is on display
        self.matchesFrames[self.activeFrame].place_forget() # remove it
        if (self.activeFrame + direction == ((self.numTeams * 2) - 2)): # if at the last matchDay
            self.matchesFrames[0].place(x = 0, y = 0, anchor = "nw")
            self.activeFrame = 0 # go back to the first matchDay
        else:
            self.matchesFrames[self.activeFrame + direction].place(x = 0, y = 0, anchor = "nw")
            self.activeFrame = self.activeFrame + direction # otherwise go to the next 

        index = 0
        for i, frame in enumerate(self.activeSim):
            if frame == 1:
                index = i
                break

        if self.activeFrame != index:
            self.matchesFrames[self.activeFrame].matchDayLabel.place_forget()
            self.matchesFrames[self.activeFrame].matchDayLabel.place(relx = 0.69, rely = 0.5, anchor = "center")
            self.matchesFrames[self.activeFrame].currentMatchDayButton.place(relx = 0.3, rely = 0.5, anchor = "center")
        else:
            self.matchesFrames[self.activeFrame].matchDayLabel.place_forget()
            self.matchesFrames[self.activeFrame].matchDayLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
            self.matchesFrames[self.activeFrame].currentMatchDayButton.place_forget()

    def simMatchDay(self):
        if (self.activeSim[self.activeFrame] == 0): # if the button is pressed on a matchDay that cant be simulated, return
            return

        try:
            with open("teams.json") as file:
                teamsData = json.load(file)

            with open("players.json") as file:
                teams = json.load(file)

            with open("leagues.json", "r") as file:
                leagues = json.load(file)
        except:
            teams = []
            teamsData = []
            leagues = []

        for league in leagues:
            if league["name"] == self.parent.name:
                matchReferees = league["referees"]
                
        matches = self.schedule[self.activeFrame] # get the matches for the matchDay
        matchDayScores = []
        matchDayInfo = []
        matchDayLineups = []
        matchDayReferees = []
        matchDayInjuries = []
        matchDayRatings = []
        matchDayPlayersOTM = []
    
        for index, match in enumerate(matches):
            homeTeam = match[0]
            awayTeam = match[1]
            referee = random.choice(matchReferees)
            matchDayReferees.append(referee)
            matchReferees.remove(referee)

            # find the team in players.json to be able to access their levels later
            for i, team in enumerate(teams):
                if team["name"] == homeTeam:
                    homeTeam = team
                    homeBasic = teamsData[i]
                if team["name"] == awayTeam:
                    awayTeam = team
                    awayBasic = teamsData[i]

            homeTeamLineup = self.getLineup(homeTeam)
            awayTeamLineup = self.getLineup(awayTeam)
            lineups = [homeTeamLineup, awayTeamLineup]

            winner = self.decideWinner(homeBasic, awayBasic) # decide who wins the game, or if its a draw
            levelDiff = abs(homeBasic["level"] - awayBasic["level"]) # difference in levels
            score = self.generateScore(winner, homeBasic, awayBasic, levelDiff) # get the score based on the winner

            redCard, redTeam = self.getReds(homeTeamLineup, awayTeamLineup, homeTeam, awayTeam, winner)
            injury, injTeam = self.getInjury(homeTeamLineup, awayTeamLineup)
            homeMissedPen = self.getMissedPens(homeTeamLineup)
            awayMissedPen = self.getMissedPens(awayTeamLineup)
            homeScorers = self.getScorers(homeTeamLineup, awayTeamLineup, score[homeTeam["name"]], redCard, homeMissedPen) 
            awayScorers = self.getScorers(awayTeamLineup, homeTeamLineup, score[awayTeam["name"]], redCard, awayMissedPen)
            homeRatings = self.getRatings(homeTeam["name"], homeScorers, awayScorers, homeTeamLineup, winner, score[awayTeam["name"]])
            awayRatings = self.getRatings(awayTeam["name"], awayScorers, homeScorers, awayTeamLineup, winner, score[homeTeam["name"]])
            matchRatings = [homeRatings, awayRatings]

            # code to remove duplicate times for any events
            combinedScorers = [(item, 'home') for item in homeScorers] + [(item, 'away') for item in awayScorers]

            uniqueTimes = set()
            adjustedScorers = []
            for item, origin in combinedScorers:
                scorer, assister, goalType, time = item
                while time in uniqueTimes:
                    if "+" not in time:
                        intTime = int(time)
                        intTime += 1  
                        time = str(intTime)
                    else:
                        mainTime, addedTime = time.split("+")
                        intAddedTime = int(addedTime.strip())
                        intAddedTime += 1
                        time = mainTime + "+ " + str(intAddedTime)

                uniqueTimes.add(time)
                adjustedScorers.append(((scorer, assister, goalType, time), origin))

            homeScorers = [item[0] for item in adjustedScorers if item[1] == 'home']
            awayScorers = [item[0] for item in adjustedScorers if item[1] == 'away']

            maxHome = max(homeRatings)
            maxAway = max(awayRatings)

            if maxHome > maxAway:
                playerOTM = homeTeamLineup[homeRatings.index(maxHome)]["name"]
            else:
                playerOTM = awayTeamLineup[awayRatings.index(maxAway)]["name"]

            matchDayPlayersOTM.append(playerOTM)
                
            imglabels = {"home": "none", "away": "none"}
            for team in ["home", "away"]:
                if redTeam == team and injTeam == team:
                    imglabels[team] = "both"
                elif redTeam == team:
                    imglabels[team] = "red"
                elif injTeam == team:
                    imglabels[team] = "inj"

            homeLabels = imglabels["home"]
            awayLabels = imglabels["away"]

            matchInfo = [homeScorers, awayScorers]

            label = self.scoreLabels[self.activeFrame][index]
            time = label.cget("text")

            label.configure(text = "[ " + str(score[homeTeam["name"]]) + " : " + str(score[awayTeam["name"]]) + " ]")
            label.bind("<Enter> <Button-1>", lambda event, label = label, time = time, homeTeam = homeBasic, awayTeam = awayBasic, matchInfo = matchInfo, lineups = lineups, matchRatings = matchRatings, referee = referee, injury = injury, playerOTM = playerOTM: self.openMatch(label, time, homeTeam, awayTeam, matchInfo, lineups, matchRatings, referee, injury, playerOTM))

            yPlaces = [60 + 50 * i for i in range(12)]
            redSrc = Image.open("Images/redCard.png")
            redCardImg = ctk.CTkImage(redSrc, None, (10, 10))
            injSrc = Image.open("Images/injury.png")
            inj = ctk.CTkImage(injSrc, None, (10, 10))

            if homeLabels != "none":
            
                if homeLabels == "red":
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = redCardImg, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                elif homeLabels == "inj":
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                else:
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = redCardImg, fg_color = GRAY, height = 10, width = 10).place(x = 155, y = yPlaces[index] - 5, anchor = "nw")
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 165, y = yPlaces[index] - 5, anchor = "nw")

            if awayLabels != "none":
                if awayLabels == "red":
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = redCardImg, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                elif awayLabels == "inj":
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                else:
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = redCardImg, fg_color = GRAY, height = 10, width = 10).place(x = 195, y = yPlaces[index] - 5, anchor = "nw")
                    ctk.CTkLabel(self.matchesFrames[self.activeFrame], text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 185, y = yPlaces[index] - 5, anchor = "nw")

            # update table, the data is in the same order as the labels are in the table (and in each entry of self.tableTeams which is important) excluding games played as that is always + 1
            team1Data = [homeTeam["name"], 1 if winner == homeTeam["name"] else 0, 1 if winner == "Draw" else 0, 1 if winner == awayTeam["name"] else 0, score[homeTeam["name"]], score[awayTeam["name"]], score[homeTeam["name"]] - score[awayTeam["name"]], 0]
            team2Data = [awayTeam["name"], 1 if winner == awayTeam["name"] else 0, 1 if winner == "Draw" else 0, 1 if winner == homeTeam["name"] else 0, score[awayTeam["name"]], score[homeTeam["name"]], score[awayTeam["name"]] - score[homeTeam["name"]], 0]

            # update the points based on the winner
            if winner == homeTeam["name"]:
                team1Data[7] = 3
                team2Data[7] = 0
            elif winner == "Draw":
                team1Data[7] = 1
                team2Data[7] = 1
            else:
                team1Data[7] = 0
                team2Data[7] = 3

            self.updateTable(team1Data)
            self.updateTable(team2Data)

            self.updatePlayersData(homeTeam, awayTeam, matchInfo, lineups, matchRatings, score, injury, playerOTM)

            matchDayScores.append([homeTeam["name"], awayTeam["name"], str(score[homeTeam["name"]]) + " : " + str(score[awayTeam["name"]])]) # add the score to the list
            matchDayInfo.append(matchInfo)
            matchDayLineups.append(lineups)
            matchDayInjuries.append(injury)
            matchDayRatings.append(matchRatings)

            self.activeSim[self.activeFrame] = 0 # set the current matchDay to not be simulated
            if (self.activeFrame != (self.numTeams * 2) - 3): # set the next matchDay to be simulated. If it was the last matchDay, do nothing as the whole list should be zeros
                self.activeSim[self.activeFrame + 1] = 1 
        
        self.updateStats()
        self.injuries.append(matchDayInjuries)
        self.referees.append(matchDayReferees)
        self.scores.append(matchDayScores) # add the scores to the self.scores list
        self.matchesInfo.append(matchDayInfo)
        self.lineups.append(matchDayLineups)
        self.ratings.append(matchDayRatings)
        self.playersOTM.append(matchDayPlayersOTM)
        self.sortTable() # sort the table
        self.updatePositions(self.activeFrame + 1)
        self.reduceMatchBans() 
        self.matchesFrames[self.activeFrame].matchDayLabel.place_forget()
        self.matchesFrames[self.activeFrame].matchDayLabel.place(relx = 0.69, rely = 0.5, anchor = "center")
        self.matchesFrames[self.activeFrame].currentMatchDayButton.place(relx = 0.3, rely = 0.5, anchor = "center")

    def reduceMatchBans(self):
        for player in self.banned:
            if player["ban"] != 0:
                player["ban"] -= 1

    def getLineup(self, team):
        players = team["players"]

        gks = [player for player in players if player['position'] == 'goalkeeper']
        defs = [player for player in players if player['position'] == 'defender']
        mids = [player for player in players if player['position'] == 'midfielder']
        fwds = [player for player in players if player['position'] == 'forward']

        lineup = self.chooseGks(gks) + self.chooseDefs(defs) + self.chooseMids(mids) + self.chooseFwds(fwds)
        return lineup
    
    def chooseGks(self, players):
        playersNoBan = [player for player in players if not any(bannedPlayer["name"] == player["name"] and bannedPlayer["ban"] != 0 for bannedPlayer in self.banned)]

        if playersNoBan != []:
            chances = [player["startingChance"] for player in playersNoBan]
            chosen = random.choices(playersNoBan, weights = chances, k = 1)

        else:
            chosen = self.generate_fake_player("goalkeeper")

        return chosen
    
    def chooseDefs(self, players):
        position1 = [player for player in players if player["startingChance"] in [0.7, 0.3]]
        position2 = [player for player in players if player["startingChance"] in [0.71, 0.29]]
        position3 = [player for player in players if player["startingChance"] in [0.72, 0.28]]
        position4 = [player for player in players if player["startingChance"] in [0.69, 0.31]]

        chosen = []
        positions = [position1, position2, position3, position4]
        for position in positions:
            playersNoBan = [player for player in position if not any(bannedPlayer["name"] == player["name"] and bannedPlayer["ban"] != 0 for bannedPlayer in self.banned)]

            if playersNoBan != []:
                chances = [player["startingChance"] for player in playersNoBan]
                player = random.choices(playersNoBan, weights = chances, k = 1)[0]
                chosen.append(player)

            else:
                chosen.append(self.generateFakePlayer("defender"))

        return chosen
    
    def chooseMids(self, players):
        position1 = [player for player in players if player["startingChance"] in [0.7, 0.3]]
        position2 = [player for player in players if player["startingChance"] in [0.71, 0.29]]
        position3 = [player for player in players if player["startingChance"] in  [0.69, 0.31]]

        chosen = []
        positions = [position1, position2, position3]
        for position in positions:
            playersNoBan = [player for player in position if not any(bannedPlayer["name"] == player["name"] and bannedPlayer["ban"] != 0 for bannedPlayer in self.banned)]

            if playersNoBan != []:
                chances = [player["startingChance"] for player in playersNoBan]
                player = random.choices(playersNoBan, weights = chances, k = 1)[0]
                chosen.append(player)

            else:
                chosen.append(self.generateFakePlayer("midfielder"))

        return chosen

    def chooseFwds(self, players):
        position1 = [player for player in players if player["startingChance"] in [0.8, 0.1]]
        position2 = [player for player in players if player["startingChance"] in [0.7, 0.3]]
        position3 = [player for player in players if player["startingChance"] in [0.71, 0.29]]

        chosen = []
        positions = [position1, position2, position3]
        for position in positions:
            playersNoBan = [player for player in position if not any(bannedPlayer["name"] == player["name"] and bannedPlayer["ban"] != 0 for bannedPlayer in self.banned)]

            if playersNoBan != []:
                chances = [player["startingChance"] for player in playersNoBan]
                player = random.choices(playersNoBan, weights = chances, k = 1)[0]
                chosen.append(player)

            else:
                chosen.append(self.generateFakePlayer("forward"))

        return chosen

    def generateFakePlayer(self, position):
        faker = Faker()
        name = faker.name_male()
        name = name.replace("Mr. ", "").replace("Dr. ", "").replace(" PhD", "").replace(" MD", "").replace(" DVM", "").replace(".", "").replace(" DDS", "")

        return {
            "name": name,
            "age": 0,
            "number": 0,
            "nationality": "none",
            "position": position,
            "startingChance": 0,
            "seasonStats": [],
            "matchBan": 0,
            "banType": "",
            "matches": [],
            "seasonsData": []
        }
    
    def getScorers(self, homeLineup, awayLineup, goals, redCardPlayer, missedPenalty):
        chances = {
            'goalkeeper': 0.01,
            'defender': 0.049,
            'midfielder': 0.25,
            'forward': 0.7
        }

        goalTypes = {
            "goal": 0.8,
            "penalty": 0.15,
            "own goal": 0.05
        }

        ownGoalChances = {
            'goalkeeper': 0.1,
            'defender': 0.8,
            'midfielder': 0.05,
            'forward': 0.05
        }

        assistChances = {
            'goalkeeper': 0.01,
            'defender': 0.3,
            'midfielder': 0.49,
            'forward': 0.2
        }

        if redCardPlayer is not None:
            homeLineupCopy = [player for player in homeLineup if player["name"] != redCardPlayer[0]]
            awayLineupCopy = [player for player in awayLineup if player["name"] != redCardPlayer[0]]
        else:
            homeLineupCopy = homeLineup
            awayLineupCopy = awayLineup

        scorers = random.choices(homeLineupCopy, weights = [chances[player['position']] for player in homeLineupCopy], k = goals)
        types = random.choices(list(goalTypes.keys()), weights = [goalTypes[goalType] for goalType in goalTypes], k = goals)
        times = random.choices(range(1, 91), k = goals)
        combinedList = [(scorer, "none", type_, time) for scorer, type_, time in zip(scorers, types, times)]

        updatedList = []
        for scorer, assister, goalType, time in combinedList:
            if goalType == "own goal":
                scorer = random.choices(awayLineupCopy, weights = [ownGoalChances[player['position']] for player in awayLineupCopy], k = 1)[0]
            if goalType == "penalty":
                forwards = [player for player in homeLineupCopy if player['position'] == 'forward']
                scorer = random.choices(forwards, weights = [chances[player['position']] for player in forwards], k = 1)[0]

            if goalType == "goal":
                lineupNoScorer = [player for player in homeLineupCopy if player["name"] != scorer["name"]]
                assister = random.choices(lineupNoScorer, weights = [assistChances[player['position']] for player in lineupNoScorer], k = 1)[0]
                assister = assister["name"]

            if time == 45 or time == 90:
                additionalTime = random.randint(0, 5)
                if additionalTime != 0:
                    time = str(time) + " + " + str(additionalTime)
            else:
                time = str(time)

            scorer = scorer["name"]

            updatedList.append((scorer, assister, goalType, str(time)))
        
        if redCardPlayer is not None:
            for player in homeLineup:
                if redCardPlayer[0] == player["name"]:
                    updatedList.append(redCardPlayer)

        if missedPenalty is not None:
            updatedList.append(missedPenalty)

        return updatedList

    def getInjury(self, homeLineup, awayLineup):
        injuryChances = {
            'home': 0.05,
            'away': 0.05,
            'none': 0.9
        }

        positionChances = {
            'goalkeeper': 0.05,
            'defender': 0.4,
            'midfielder': 0.3,
            'forward': 0.25
        }

        injuryTeam = random.choices(list(injuryChances.keys()), weights = list(injuryChances.values()), k = 1)[0]

        if injuryTeam != 'none':
            injuryPosition = random.choices(list(positionChances.keys()), weights = list(positionChances.values()), k = 1)[0]

            lineup = homeLineup if injuryTeam == 'home' else awayLineup
            injuredPlayer = random.choice([player for player in lineup if player["position"] == injuryPosition])

            if injuredPlayer["startingChance"] != 0: # if it is zero, it is a new player created just for that game due to all players for a position being unable to play
                self.addMatchBan(injuredPlayer["name"], "injury")

            return injuredPlayer["name"], injuryTeam
    
        return 'none', 'none'

    def getReds(self, homeLineup, awayLineup, home, away, winner):
        positionChances = {
            'goalkeeper': 0.1,
            'defender': 0.05,
            'midfielder': 0.05,
            'forward': 0.8
        }

        redCardChances = {
            "home": 0.005 if home == winner else 0.06,
            "away": 0.005 if away == winner else 0.06,
            'none': 0.935
        }

        if winner == home["name"]:
            winnerSide = "home"
        else:
            winnerSide = "away"

        redCardTeam = random.choices(list(redCardChances.keys()), weights = list(redCardChances.values()), k = 1)[0]

        if redCardTeam != 'none':
            redCardPosition = random.choices(list(positionChances.keys()), weights = list(positionChances.values()), k = 1)[0]

            lineup = homeLineup if redCardTeam == "home" else awayLineup
            redCardPlayer = random.choice([player for player in lineup if player['position'] == redCardPosition])

            if redCardTeam == winnerSide:
                time = random.choices(range(60, 91), k = 1)[0]
            else:
                time = random.choices(range(1, 91), k = 1)[0]

            if time == 45 or time == 90:
                additionalTime = random.randint(0, 5)
                if additionalTime != 0:
                    time = str(time) + " + " + str(additionalTime)
            else:
                time = str(time)

            if redCardPlayer["startingChance"] != 0:
                self.addMatchBan(redCardPlayer["name"], "red")

            return (redCardPlayer["name"], "none", 'red card', str(time)), redCardTeam

        return None, 'none'

    def getMissedPens(self, lineup):
        chances = {
            "yes": 0.1,
            "no": 0.9
        }

        missed = random.choices(list(chances.keys()), weights = list(chances.values()), k = 1)[0]

        if missed == "yes":
            penaltyTaker = random.choice([player for player in lineup if player["position"] == "forward"])
            time = random.choices(range(1, 91), k = 1)[0]

            if time == 45 or time == 90:
                additionalTime = random.randint(0, 5)
                if additionalTime != 0:
                    time = str(time) + " + " + str(additionalTime)
            else:
                time = str(time)

            return (penaltyTaker["name"], "none", "missed penalty", str(time))
        else:
            return None

    def addMatchBan(self, playerName, type_):
        if type_ == "red":
            bans = [2, 3]
            ban = random.choice(bans)
            # ban = 0
        else:
            bans = [5, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 9, 10, 15]
            ban = random.choice(bans)
            # ban = 0

        newBan = {
            "name": playerName,
            "ban": ban,
            "type": type_,
            "compName": self.parent.name
        }

        self.banned.append(newBan)

    def getRatings(self, teamName, scorersHome, scorersAway, lineup, winner, awayGoals):

        if winner == teamName:
            ratings = [7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00, 7.00]
        elif winner == "draw":
            ratings = [6.50, 6.50, 6.50, 6.50, 6.50, 6.50, 6.50, 6.50, 6.50, 6.50, 6.50]
        else:
            ratings = [6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00, 6.00]

        for i, player in enumerate(lineup):
            scorerFlag = False
            for scorer in scorersHome:
                if scorer[0] == player["name"]: 
                    if scorer[2] == "goal":
                        ratings[i] += random.choice([1.00, 1.12, 1.05, 1.15, 1.07, 1.01, 1.04, 1.11])
                    elif scorer[2] == "penalty":
                        ratings[i] += random.choice([0.75, 0.78, 0.82, 0.84, 0.90, 0.94, 1.03, 1.08])
                    elif scorer[2] == "red card":
                        ratings[i] -= random.choice([2.89, 3.15, 3.22, 3.27, 3.43, 3.52, 3.65, 3.76])
                    else: # missed penalty
                        ratings[i] -= random.choice([0.32, 0.41, 0.47, 0.54, 0.55, 0.59, 0.63, 0.67])
                
                if scorer[1] == player["name"]: # assist
                    ratings[i] += random.choice([0.78, 0.82, 0.85, 0.89, 0.94, 0.98, 1.03, 1.08])

                    scorerFlag = True

            if not scorerFlag:
                if player["position"] == "goalkeeper" or player["position"] == "defender":
                    if awayGoals <= 1:
                        ratings[i] += random.choice([0.32, 0.42, 0.47, 0.63, 0.69, 0.78, 0.85, 0.98])
                    elif awayGoals <= 3:
                        ratings[i] += random.choice([0.02, 0.08, 0.15, 0.19, 0.24, 0.29, 0.36, 0.45])
                    else:
                        ratings[i] -= random.choice([0.89, 0.92, 0.97, 1.03, 1.09, 1.15, 1.22, 1.29])
                
                else: # mids and fwds that didnt score or get a red
                    ratings[i] += random.choice([-0.56, -0.43, -0.32, -0.21, -0.19, 0.05, 0.09, 0.13, 0.17, 0.24, 0.31, 0.46, 0.49, 0.67])

            for scorer in scorersAway:
                if scorer[0] == player["name"]: # own goal
                    ratings[i] -= random.choice([1.46, 1.49, 1.52, 1.57, 1.60, 1.63, 1.69, 1.78])
        
        ratings = [min(round(rating, 2), 10) for rating in ratings]
        return ratings

    def updatePlayersData(self, homeTeam, awayTeam, matchInfo, lineups, matchRatings, score, injuredPlayer, playerOTM):
        for i, lineup in enumerate(lineups): # home then away
            teamName = homeTeam["name"] if i == 0 else awayTeam["name"]
            for team in self.playersData:
                if team["name"] == teamName:
                    teamList = team
                    break
            
            for j, player in enumerate(lineup):
                playerGoals = 0
                playerAssists = 0
                playerReds = 0
                playerCleanSheet = 0
                playerOwn = 0
                playerRating = 0.00
                playerPens = 0
                injured = False
                playerOfTM = False
                
                for data in matchInfo:
                    for scorer in data:
                        if scorer[0] == player["name"]:
                            if scorer[2] == "goal":
                                playerGoals += 1
                            elif scorer[2] == "penalty":
                                playerGoals += 1
                                playerPens += 1
                            elif scorer[2] == "own goal":
                                playerOwn += 1
                            else:
                                playerReds += 1
                        
                        elif scorer[1] == player["name"]:
                            playerAssists += 1

                playerRating = matchRatings[i][j]

                if injuredPlayer == player["name"]:
                    injured = True

                if playerOTM == player["name"]:
                    playerOfTM = True

                for team in score:
                    if team != teamName:
                        if score[team] == 0:
                            playerCleanSheet = 1

                playerFound = False 
                for entry in teamList["players"]:
                    if entry["name"] == player["name"]:
                        playerMatches = entry["matches"]
                        playerSeasonData = entry["seasonStats"]
                        playerFound = True
                        break 

                if not playerFound: # if the player is a fake player created as no players were available for a position
                    newPlayer = {
                        "name": player["name"],
                        "matches": [],
                        "seasonStats": []
                    }
                    playerMatches = newPlayer["matches"]
                    playerSeasonData = newPlayer["seasonStats"]
                    teamList["players"].append(newPlayer)

                matchEntry = {
                    "against": awayTeam["name"] if i == 0 else homeTeam["name"],
                    "score": score,
                    "goals": playerGoals,
                    "assists": playerAssists,
                    "own goals": playerOwn,
                    "red": playerReds,
                    "clean sheet": playerCleanSheet,
                    "rating": playerRating,
                    "injured": injured,
                    "playerOTM": playerOfTM,
                    "compName": self.parent.name
                }

                if playerSeasonData != []:
                    for comp in playerSeasonData:
                        if comp["compName"] == self.parent.name:
                            comp["played"] += 1
                            comp["goals"] += playerGoals
                            comp["assists"] += playerAssists
                            comp["reds"] += playerReds
                            comp["clean sheets"] += playerCleanSheet
                            comp["averageRating"] = round((comp["averageRating"] * (comp["played"] - 1) + playerRating) / comp["played"], 2)
                            # playerSeasonData[0]["averageRating"] = round((playerSeasonData[0]["averageRating"] + playerRating) / 2, 2)
                            comp["pens"] += playerPens

                            if playerOfTM:
                                comp["MOTM"] += 1

                playerMatches.append(matchEntry)

    def updateStats(self):
        # find the top scorer and top assister
        topScorersHeap = []
        topAssistersHeap = []
        topRatingsHeap = []
        topCleanSheetsHeap = []
        topPensHeap = []
        topPOTMHeap = []

        numMatchdays = (self.numTeams * 2) - 2
        averageRatingBaseline = numMatchdays / 8  # players need to have played at least 1/8 of the games to be considered for the top average rating

        compIndex = None
        for team in self.playersData:
            for player in team["players"]:
                if player["seasonStats"] != []:

                    if compIndex is None:
                        for comp in player["seasonStats"]:
                            if comp["compName"] == self.parent.name:
                                compIndex = player["seasonStats"].index(comp)

                    seasonStats = player["seasonStats"][compIndex]

                    if seasonStats["goals"] != 0:
                        entry = {
                            "name": player["name"],
                            "stat": seasonStats["goals"],
                            "team": team["name"]
                        }

                        if len(topScorersHeap) < 7:  # If the heap has less than 7 elements, push the new entry
                            heapq.heappush(topScorersHeap, (seasonStats["goals"], player["name"], entry))
                        else:  # If the new entry has more goals than the smallest element in the heap, replace it
                            if seasonStats["goals"] > topScorersHeap[0][0]:
                                heapq.heapreplace(topScorersHeap, (seasonStats["goals"], player["name"], entry))

                    if seasonStats["assists"] != 0:
                        entry = {
                            "name": player["name"],
                            "stat": seasonStats["assists"],
                            "team": team["name"]
                        }

                        if len(topAssistersHeap) < 7:
                            heapq.heappush(topAssistersHeap, (seasonStats["assists"], player["name"], entry))
                        else:
                            if seasonStats["assists"] > topAssistersHeap[0][0]:
                                heapq.heapreplace(topAssistersHeap, (seasonStats["assists"], player["name"], entry))

                    matchDay = self.activeFrame + 1
                    entry = {
                            "name": player["name"],
                            "stat": seasonStats["averageRating"],
                            "team": team["name"]
                        }

                    if matchDay > 5 and seasonStats["played"] > averageRatingBaseline:
                        if len(topRatingsHeap) < 7:
                            heapq.heappush(topRatingsHeap, (seasonStats["averageRating"], player["name"], entry))
                        else:
                            if seasonStats["averageRating"] > topRatingsHeap[0][0]:
                                heapq.heapreplace(topRatingsHeap, (seasonStats["averageRating"], player["name"], entry))
                    elif matchDay <= 5:
                        if len(topRatingsHeap) < 7:
                            heapq.heappush(topRatingsHeap, (seasonStats["averageRating"], player["name"], entry))
                        else:
                            if seasonStats["averageRating"] > topRatingsHeap[0][0]:
                                heapq.heapreplace(topRatingsHeap, (seasonStats["averageRating"], player["name"], entry))

                    if seasonStats["MOTM"] != 0:
                        entry = {
                            "name": player["name"],
                            "stat": seasonStats["MOTM"],
                            "team": team["name"]
                        }

                        if len(topPOTMHeap) < 7:
                            heapq.heappush(topPOTMHeap, (seasonStats["MOTM"], player["name"], entry))
                        else:
                            if seasonStats["MOTM"] > topPOTMHeap[0][0]:
                                heapq.heapreplace(topPOTMHeap, (seasonStats["MOTM"], player["name"], entry))

                    if player["position"] == "goalkeeper":
                        entry = {
                            "name": player["name"],
                            "stat": seasonStats["clean sheets"],
                            "team": team["name"]
                        }

                        if len(topCleanSheetsHeap) < 7:
                            heapq.heappush(topCleanSheetsHeap, (seasonStats["clean sheets"], player["name"], entry))
                        else:
                            if seasonStats["clean sheets"] > topCleanSheetsHeap[0][0]:
                                heapq.heapreplace(topCleanSheetsHeap, (seasonStats["clean sheets"], player["name"], entry))

                    if player["position"] == "forward":
                        entry = {
                            "name": player["name"],
                            "stat": seasonStats["pens"],
                            "team": team["name"]
                        }

                        if len(topPensHeap) < 7:
                            heapq.heappush(topPensHeap, (seasonStats["pens"], player["name"], entry))
                        else:
                            if seasonStats["pens"] > topPensHeap[0][0]:
                                heapq.heapreplace(topPensHeap, (seasonStats["pens"], player["name"], entry))

        # Convert heaps to sorted lists of top players
        topScorers = [heapq.heappop(topScorersHeap)[2] for _ in range(len(topScorersHeap))]
        topScorers.reverse()

        topAssisters = [heapq.heappop(topAssistersHeap)[2] for _ in range(len(topAssistersHeap))]
        topAssisters.reverse()

        topAverageRatings = [heapq.heappop(topRatingsHeap)[2] for _ in range(len(topRatingsHeap))]
        topAverageRatings.reverse()

        topCleanSheets = [heapq.heappop(topCleanSheetsHeap)[2] for _ in range(len(topCleanSheetsHeap))]
        topCleanSheets.reverse()

        topPens = [heapq.heappop(topPensHeap)[2] for _ in range(len(topPensHeap))]
        topPens.reverse()

        topPOTM = [heapq.heappop(topPOTMHeap)[2] for _ in range(len(topPOTMHeap))]
        topPOTM.reverse()

        # Update the class attributes
        self.topScorer = topScorers
        self.topAssister = topAssisters
        self.topAverageRating = topAverageRatings
        self.topCleanSheet = topCleanSheets
        self.topPen = topPens
        self.topPOTM = topPOTM

        self.parent.statsMenu.updateStats(self.topScorer, self.topAssister, self.topAverageRating, self.topCleanSheet, self.topPen, self.topPOTM)

    def openMatch(self, label, time, home, away, matchInfo, lineups, ratings, referee, injuredPlayer, playerOTM, imported = False):
        matchInfoFrame = ctk.CTkFrame(self, fg_color = GRAY)
        matchInfoFrame.pack(expand = True, fill = "both")
        self.matchesFrames[self.activeFrame].pack_forget()
    
        backButton = ctk.CTkButton(matchInfoFrame, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBackToMatches(matchInfoFrame))
        backButton.place(x = 2, y = 2, anchor = "nw")

        homesrc = Image.open("SavedImages/Teams/" + home["name"] + ".png")
        homeLogo = ctk.CTkImage(homesrc, None, (50, 50))
        ctk.CTkLabel(matchInfoFrame, text = "", image = homeLogo, fg_color = GRAY).place(x = 100, y = 50, anchor = "center")
        ctk.CTkLabel(matchInfoFrame, text = home["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 100, y = 100, anchor = "center")

        awaysrc = Image.open("SavedImages/Teams/" + away["name"] + ".png")
        awayLogo = ctk.CTkImage(awaysrc, None, (50, 50))
        ctk.CTkLabel(matchInfoFrame, text = "", image = awayLogo, fg_color = GRAY).place(x = 270, y = 50, anchor = "center")
        ctk.CTkLabel(matchInfoFrame, text = away["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 270, y = 100, anchor = "center")

        ctk.CTkLabel(matchInfoFrame, text = label.cget("text"), fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 25)).place(x = 185, y = 50, anchor = "center")
        
        scorersFrame = ctk.CTkFrame(matchInfoFrame, fg_color = GRAY, height = 180, width = 355)
        scorersFrame.place(x = 5, y = 115, anchor = "nw")

        xPlaces = [139, 155, 200, 215]
        yPlaces = [0, 22, 44, 66, 88, 110, 132, 154, 176]
        for j, team in enumerate(matchInfo):
            if not imported:
                team = sorted(team, key = lambda x: int(str(x[3]).split("+")[0]) + int(str(x[3]).split("+")[1]) if "+" in str(x[3]) else int(x[3]))
            else:
                team = sorted(team, key = lambda x: int(str(x["time"]).split("+")[0]) + int(str(x["time"]).split("+")[1]) if "+" in str(x["time"]) else int(x["time"]))

            for i, scorer in enumerate(team):
                if not imported:
                    goalScorer = scorer[0]
                    assister = scorer[1]
                    type_ = scorer[2]
                    goalTime = scorer[3]
                else:
                    goalScorer = scorer["name"]
                    type_ = scorer["type"]
                    goalTime = scorer["time"]

                if type_ == "goal":
                    src = Image.open("Images/goal.png")
                elif type_ == "penalty":
                    src = Image.open("Images/penalty.png")
                elif type_ == "own goal":
                    src = Image.open("Images/ownGoal.png")
                elif type_ == "red card":
                    src = Image.open("Images/redCard.png")
                else:
                    src = Image.open("Images/missedPen.png")

                scorerName = goalScorer.split()
                
                if "Jr" in scorerName[-1] or "Sr" in scorerName[-1]:
                    lastName = scorerName[0]
                elif re.search(r'\b(?:I{1,3})\b', scorerName[-1], re.IGNORECASE): # check if the last name is a roman numeral
                    lastName = scorerName[1]
                else:
                    lastName = scorerName[-1]
                
                if j == 0:
                    label = str(goalTime) + "'  " + str(lastName)
                    ctk.CTkLabel(scorersFrame, text = label, text_color = "black", font = (APP_FONT, 12)).place(x = xPlaces[0], y = yPlaces[i], anchor = "ne")

                    goalType = ctk.CTkImage(src, None, (10, 10))
                    ctk.CTkLabel(scorersFrame, text = "", image = goalType).place(x = xPlaces[1], y = yPlaces[i], anchor = "ne")
                else:
                    label = str(lastName) + "  " + str(goalTime) + "'"
                    ctk.CTkLabel(scorersFrame, text = label, text_color = "black", font = (APP_FONT, 12)).place(x = xPlaces[3], y = yPlaces[i], anchor = "nw")

                    goalType = ctk.CTkImage(src, None, (10, 10))
                    ctk.CTkLabel(scorersFrame, text = "", image = goalType).place(x = xPlaces[2], y = yPlaces[i], anchor = "nw")

        mostGoals = 0
        if len(matchInfo[0]) > len(matchInfo[1]):
            mostGoals = len(matchInfo[0])
        else: mostGoals = len(matchInfo[1])
    
        lineupFrame = ctk.CTkFrame(matchInfoFrame, fg_color = GRAY, height = 250, width = 355)
        lineupFrame.place(x = 5, y = 130 + yPlaces[mostGoals], anchor = "nw")
        endOfFrame = 390 + yPlaces[mostGoals]

        ctk.CTkLabel(lineupFrame, text = "Lineups", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(relx = 0.5, y = 10, anchor = "center")

        ySpaces = [30, 51, 72, 93, 114, 135, 156, 177, 198, 219, 240]
        for i, lineup in enumerate(lineups):
            for j, name in enumerate(lineup):
                if not imported:
                    text = name["name"]
                else:
                    text = name

                if i == 0:
                    playerX = 70
                    ratingX = 157
                    y = ySpaces[j]
                elif i == 1:
                    playerX = 285
                    ratingX = 197
                    y = ySpaces[j]

                if text == playerOTM:
                    if text != injuredPlayer:
                        ctk.CTkLabel(lineupFrame, text = text + " *", fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")
                    else:
                        ctk.CTkLabel(lineupFrame, text = text + " (inj) *", fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")
                elif text == injuredPlayer:
                    ctk.CTkLabel(lineupFrame, text = text + " (inj)", fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")
                else:
                    ctk.CTkLabel(lineupFrame, text = text, fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")

                ctk.CTkLabel(lineupFrame, text = ratings[i][j], fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = ratingX, y = y, anchor = "center")

        src = Image.open("Images/bulletPoint.png")
        bulletPoint = ctk.CTkImage(src, None, (10, 10))

        for i in range(2):
            ctk.CTkLabel(matchInfoFrame, text = "", image = bulletPoint, fg_color = GRAY).place(x = 15, y = endOfFrame + (i * 20))
            ctk.CTkLabel(matchInfoFrame, text = "", image = bulletPoint, fg_color = GRAY).place(x = 205, y = endOfFrame + (i * 20))
        
        ctk.CTkLabel(matchInfoFrame, text = home["stadium"], fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 30, y = endOfFrame, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = time, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 220, y = endOfFrame, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = self.parent.name, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 30, y = endOfFrame + 20, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = referee,  fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 220, y = endOfFrame + 20, anchor = "nw")

    def goBackToMatches(self, frame):
        frame.pack_forget()
        self.matchesFrames[self.activeFrame].place(x = 0, y = 0, anchor = "nw")

    def getProbability(self, levelDiff, probType):
        # this function is called by decideWinner

        # Define the points to interpolate between
        points = [(0, 33.3, 33.3), (10, 25, 60), (20, 15, 75), (30, 15, 70), (40, 10, 80), (50, 5, 90), (60, 2, 95), (70, 1, 98), (80, 0.5, 99), (90, 0.25, 99.5)]

        # Find the interval that level_diff falls into
        for i in range(len(points) - 1):
            x1, y1, z1 = points[i]
            x2, y2, z2 = points[i + 1]
            if x1 <= levelDiff < x2:
                # Linearly interpolate between the two points
                if probType == "draw":
                    return ((y2 - y1) * (levelDiff - x1) / (x2 - x1) + y1) / 100
                elif probType == "win":
                    return ((z2 - z1) * (levelDiff - x1) / (x2 - x1) + z1) / 100

        # If level_diff is greater than the largest x-value, return the y-value or z-value of the last point
        x, y, z = points[-1]
        if probType == "draw":
            return y / 100
        elif probType == "win":
            return z / 100
    
    def decideWinner(self, team1, team2, advantage = True):
        if advantage: # home advantage
            homeAdvantage = 5  # Define the home advantage
            levelDiff = team2["level"] - (team1["level"] + homeAdvantage)  # Add the home advantage to team1's level
        else:
            levelDiff = team2["level"] - team1["level"]

        probDraw = self.getProbability(abs(levelDiff), "draw") # get the probability of a draw

        if levelDiff < 0:  # team1 has a higher level
            probTeam1 = self.getProbability(-levelDiff, "win")
            probTeam2 = 1 - probDraw - probTeam1
        else:  # team2 has a higher level or levels are equal
            probTeam2 = self.getProbability(levelDiff, "win")
            probTeam1 = 1 - probDraw - probTeam2

        rand_num = random.random() # generate a random number between 0 and 1

        # if the random number is less than the probability of team1 winning, team1 wins
        if rand_num < probTeam1:
            winner = team1["name"]
        elif rand_num < probTeam1 + probDraw: # if the random number is less than the probability of a draw and team 1 winning, it's a draw
            winner = "Draw"
        else: # else team 2 wins
            winner = team2["name"]

        return winner
        
    def generateScore(self, winner, team1, team2, levelDiff):
        # this function uses lists to get scores. The more there is of a number, the more likely it is that that number will be chosen
        if winner == "Draw":
            # If it's a draw, both teams score the same number of goals
            goalChoices = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 5]
            goals = random.choice(goalChoices)
            return {team1["name"]: goals, team2["name"]: goals}
        else:
            winningTeam = team1 if winner == team1["name"] else team2
            losingTeam = team2 if winner == team1["name"] else team1

        # Check if the winning team has a lower level as if it does, it should realistically not score many goals
        if winningTeam["level"] < losingTeam["level"]:
            # Limit the maximum number of goals that the winning team can score
            winningGoalsChoices = [1, 2, 2, 2, 3, 3]
            losingGoalsChoices = [0, 1, 1, 1, 2]
        else:
            # Use different lists for winningGoalsChoices based on the level difference (the higher the difference, the possibility to score a lot of goals)
            if levelDiff < 10:
                winningGoalsChoices = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3]
                losingGoalsChoices = [0, 1, 1, 2]
            elif levelDiff <= 20:
                winningGoalsChoices = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]
                losingGoalsChoices = [0, 1, 1, 2, 2, 3]
            elif levelDiff < 30:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2, 2]
            elif levelDiff > 100:
                winningGoalsChoices = [5, 5, 5, 5, 6, 6, 6, 7, 7]
                losingGoalsChoices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            else:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 7, 7]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2]
    
        # get the score
        winningGoals = random.choice(winningGoalsChoices)
        losingGoals = random.choice(losingGoalsChoices)

        # if the goals scored by the losing team is more than the winning team, get a score until it isn't
        while losingGoals >= winningGoals:
            losingGoals = random.choice(losingGoalsChoices)

        return {team1["name"]: winningGoals if winningTeam == team1 else losingGoals, 
                team2["name"]: losingGoals if winningTeam == team1 else winningGoals}

    def createMatches(self):
        if self.parent.tableMenu.tableTeams != []: # make sure that teams were added to the league, otherwise do nothing
            numTeams = str((self.parent.numTeams * 2) - 2)
            progressLabel = ctk.CTkLabel(self, text = "Matchdays created: 0 / " + numTeams, font = (APP_FONT, 20), text_color  = "white")
            progressLabel.place(x = 185, y = 350, anchor = "center")
            progressLabel.update_idletasks()

            self.createFrames()

            try:
                with open("players.json", "r") as file:
                    players = json.load(file)
            except:
                players = []

            times = ["12:30", "13:00", "14:00", "15:00", "17:00", "19:00", "20:00"]
            teamNames = [] # get the names of all the teams in the league
            for team in self.parent.tableMenu.tableTeams:
                teamNames.append(team[0].cget("text"))

                entry = {
                    "name": team[0].cget("text"),
                    "players": []
                }

                for teamPlayers in players:
                    if teamPlayers["name"] == team[0].cget("text"):
                        for player in teamPlayers["players"]:
                            entry["players"].append(player)

                self.playersData.append(entry)

            random.shuffle(teamNames)

            ## algorithm generated by co-pilot: round-robin algorithm to create the matchdays
            for i in range(len(teamNames) - 1):
                pairs = []
                for j in range(len(teamNames) // 2):
                    # Alternate home and away games
                    if i % 2 == 0:
                        pairs.append((teamNames[j], teamNames[- j - 1], random.choice(times)))
                    else:
                        pairs.append((teamNames[- j - 1], teamNames[j], random.choice(times)))
                teamNames.insert(1, teamNames.pop())
                self.schedule.append(pairs)

            self.schedule = [[pair for pair in day if pair[1]] for day in self.schedule]

            second_round = [[(away, home, time) for home, away, time in day] for day in self.schedule]
            self.schedule += second_round
            ## end of algorithm

            for i in range(len(self.schedule)): # sort each matchDay by time
                self.schedule[i] = sorted(self.schedule[i], key = lambda match: match[2])

            # add the matches to each frame
            for i, day in enumerate(self.schedule):
                frame = self.matchesFrames[i]
        
                labels = []
                for index, match in enumerate(day): # for each match in the matchday
                    teamHome = match[0]
                    teamAway = match[1]
                    time = match[2]

                    srcHome = Image.open("SavedImages/Teams/" + teamHome + ".png")
                    logoHome = ctk.CTkImage(srcHome, None, (30, 30))

                    srcAway = Image.open("SavedImages/Teams/" + teamAway + ".png")
                    logoAway = ctk.CTkImage(srcAway, None, (30, 30))

                    yPlaces = [60 + 50 * i for i in range(12)]
                    xPlaces = [105, 145, 180, 215, 255]

                    ctk.CTkLabel(frame, text = match[0], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(match[0]) > 15 else 12)).place(x = xPlaces[0], y = yPlaces[index], anchor = "ne")
                    ctk.CTkLabel(frame, text = "", image = logoHome, fg_color = GRAY).place(x = xPlaces[1], y = yPlaces[index], anchor = "ne")
                    scoreLabel = ctk.CTkLabel(frame, text = time, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))
                    scoreLabel.place(x = xPlaces[2], y = yPlaces[index] + 15, anchor = "center")
                    ctk.CTkLabel(frame, text = "", image = logoAway, fg_color = GRAY).place(x = xPlaces[3], y = yPlaces[index], anchor = "nw")
                    ctk.CTkLabel(frame, text = match[1], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(match[1]) > 15 else 12)).place(x = xPlaces[4], y = yPlaces[index], anchor = "nw")

                    labels.append(scoreLabel)
                
                progressLabel.configure(text = "Matchdays created: " + str(i + 1) + " / " + numTeams)
                progressLabel.update_idletasks()
                self.scoreLabels.append(labels)

            progressLabel.destroy()
            
            self.activeSim[0] = 1
            self.saveMatches() # save the matches to the leaguesData.json file
            self.matchesFrames[0].place(x = 0, y = 0, anchor = "nw") # place the first frame
            self.actionButtonsFrame.place(x = 0, y = 585, anchor = "nw")

    def updateTable(self, teamData):
        for team in self.parent.tableMenu.tableTeams: # loop through the list
            if team[0].cget("text") == teamData[0]: # find the correct teams
                team[1].configure(text = str(int(team[1].cget("text")) + 1)) # add 1 to its number of games played

                for i in range(1, 8): # adjust the rest of the data accordingly
                    team[i + 1].configure(text = str(int(team[i + 1].cget("text")) + teamData[i]))

                for teamEntry in self.points:
                    if teamEntry == team[0].cget("text"):
                        self.points[teamEntry].append(int(team[8].cget("text")))
        
    def updatePositions(self, matchDay):
        for index, team in enumerate(self.parent.tableMenu.tableTeams):
            for teamName in self.positions:
                if team[0].cget("text") == teamName:
                    self.positions[teamName].append(index + 1)
                                                    
        if matchDay >= 2:
            graphsMenu = self.parent.graphsMenu
            graphsMenu.canvas.delete()
            graphsMenu.canvas = ctk.CTkCanvas(graphsMenu.canvasFrame, bg = GRAY, width = graphsMenu.canvasWidth, height = graphsMenu.canvasHeight, highlightthickness = 0)
            graphsMenu.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

            if graphsMenu.graph == "positions":
                graphsMenu.drawGrid(matchDay - 1)

                for i, team in enumerate(self.positions):
                    src = "SavedImages/Teams/" + team + ".png"
                    graphsMenu.addPoints(self.positions[team], src, matchDay - 1, i)
            else:
                mostPoints = max(x[-1] for x in self.points.values())
                graphsMenu.rows = int(mostPoints)
                graphsMenu.drawGrid(matchDay - 1)

                for i, team in enumerate(self.points):
                    src = "SavedImages/Teams/" + team + ".png"
                    graphsMenu.addPoints(self.points[team], src, matchDay - 1, i)

    def sortTable(self, points = True):
        tableTeams = self.parent.tableMenu.tableTeams
        tableLogos = self.parent.tableMenu.tableLogos

        if(points == True): # sort by points, then by goal difference and then goals scored
            sortedTeams = sorted(tableTeams, key = lambda x: (int(x[8].cget("text")), int(x[7].cget("text")), int(x[5].cget("text"))), reverse = True) 
        else: # sort alphabetically
            sortedTeams = sorted(tableTeams, key = lambda x: x[0].cget("text")) 

        # Create a list of the text values from sortedTeams
        sortedTexts = [[label.cget("text") for label in team] for team in sortedTeams]

        try:
            with open("teams.json", "r") as file:
                teams = json.load(file)
        except:
            teams = []
        
        for i, sortedTeam in enumerate(sortedTeams): # loop through the sorted teams
            for j in range(len(sortedTeam)): # loop through the labels in the team
                tableTeams[i][j].configure(text = sortedTexts[i][j]) # update the label to one in sortedTexts

                # change the team's logo
                for team in teams:
                    if team["name"] == sortedTexts[i][j]:
                        src = Image.open(team["logoPath"])
                        logo = ctk.CTkImage(src, None, (20, 20))
                        tableLogos[i].configure(image = logo)

    def saveTable(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)

            with open("players.json", "r") as file:
                teamsData = json.load(file)
        except:
            leaguesData = []
            teamsData = []
        
        for league in leaguesData: # find the league in leaguesData.json
            if league["name"] == self.parent.name:
                league["topScorer"] = self.topScorer
                league["topAssister"] = self.topAssister
                league["topAverageRating"] = self.topAverageRating
                league["topCleanSheet"] = self.topCleanSheet
                league["topPen"] = self.topPen
                league["topPOTM"] = self.topPOTM
                teams = league["teams"] # get its teams
                matchDays = league["matchDays"] # and matchDay
                break
        
        if hasattr(self.parent.tableMenu, "tableTeams"): # if teams were created
            for teamData in self.parent.tableMenu.tableTeams: 
                for team in teams: # loop through the teams
                    if team["name"] == teamData[0].cget("text"): # find the correct team and update the data
                        team["gp"] = teamData[1].cget("text")
                        team["w"] = teamData[2].cget("text")
                        team["d"] = teamData[3].cget("text")
                        team["l"] = teamData[4].cget("text")
                        team["gf"] = teamData[5].cget("text")
                        team["ga"] = teamData[6].cget("text")
                        team["gd"] = teamData[7].cget("text")
                        team["p"] = teamData[8].cget("text")

                        team["positions"] = self.positions[team["name"]]
                        team["points"] = self.points[team["name"]]

        for i, matchDay in enumerate(matchDays):
            for matches in matchDay["matches"]: # loop through each match through each matchDay
                for matchDayScores in self.scores: # loop through the scores
                    for j, match in enumerate(matchDayScores):
                        if match[0] == matches["home"] and match[1] == matches["away"] and matches["played"] == 0: # if found the right match and the score hasnt been saved, save it
                            matches["score"] = match[2]
                            matches["played"] = 1

                            for (player, rating) in zip(self.lineups[i][j][0], self.ratings[i][j][0]):
                                entry = {
                                    "name": player["name"],
                                    "rating": rating
                                }
                                matches["homeLineup"].append(entry)

                            for (player, rating) in zip(self.lineups[i][j][1], self.ratings[i][j][1]):
                                entry = {
                                    "name": player["name"],
                                    "rating": rating
                                }
                                matches["awayLineup"].append(entry)

                            scorers = sorted(self.matchesInfo[i][j][0], key = lambda x: int(str(x[3]).split("+")[0]) + int(str(x[3]).split("+")[1]) if "+" in str(x[3]) else int(x[3]))
                            for scorer in scorers:
                                entry = {
                                    "name": scorer[0],
                                    "assister": scorer[1],
                                    "type": scorer[2],
                                    "time": scorer[3]
                                }
                                matches["homeScorers"].append(entry)

                            scorers = sorted(self.matchesInfo[i][j][1], key = lambda x: int(str(x[3]).split("+")[0]) + int(str(x[3]).split("+")[1]) if "+" in str(x[3]) else int(x[3]))
                            for scorer in scorers:
                                entry = {
                                    "name": scorer[0],
                                    "assister": scorer[1],
                                    "type": scorer[2],
                                    "time": scorer[3]
                                }
                                matches["awayScorers"].append(entry)

                            matches["referee"] = self.referees[i][j]
                            matches["injured"] = self.injuries[i][j]
                            matches["playerOTM"] = self.playersOTM[i][j]

        with open("leaguesData.json", "w") as file:
            json.dump(leaguesData, file)
        for team in teamsData:
            if hasattr(self.parent.tableMenu, "tableTeams"):
                for teamName in self.parent.tableMenu.tableTeams:
                    if team["name"] == teamName[0].cget("text"):
                        
                        teamList = None
                        for data in self.playersData:
                            if data["name"] == team["name"]:
                                teamList = data
                                break

                        for player in team["players"]:
                            for bannedPlayer in self.banned:
                                if bannedPlayer["name"] == player["name"]:
                                    for ban in player["matchBan"]:
                                        if bannedPlayer["type"] == "injury":
                                            if ban["banType"] == "injury" or ban["compName"] == bannedPlayer["compName"]:
                                                ban["ban"] = bannedPlayer["ban"]
                                                ban["banType"] = bannedPlayer["type"] if bannedPlayer["ban"] != 0 else "none"
                                        elif bannedPlayer["type"] == "red":
                                            if ban["compName"] == self.parent.name:
                                                ban["ban"] = bannedPlayer["ban"]
                                                ban["banType"] = bannedPlayer["type"] if bannedPlayer["ban"] != 0 else "none"
                        
                            if teamList is not None:
                                for playerData in teamList["players"]:
                                    if playerData["name"] == player["name"]:
                                        # player["matches"].extend(playerData["matches"])
                                        player["matches"] = playerData["matches"]

                                        for comp in player["seasonStats"]:
                                            compIndex = player["seasonStats"].index(comp)
                                            if comp["compName"] == self.parent.name:
                                                comp["played"] = playerData["seasonStats"][compIndex]["played"]
                                                comp["goals"] = playerData["seasonStats"][compIndex]["goals"]
                                                comp["assists"] = playerData["seasonStats"][compIndex]["assists"]
                                                comp["reds"] = playerData["seasonStats"][compIndex]["reds"]
                                                comp["clean sheets"] = playerData["seasonStats"][compIndex]["clean sheets"]
                                                comp["averageRating"] = playerData["seasonStats"][compIndex]["averageRating"]
                                                # comp["averageRating"] = round((averageRating + comp["averageRating"]) / 2, 2) if comp["averageRating"] != compIndex else round(averageRating, 2)
                                                comp["pens"] = playerData["seasonStats"][compIndex]["pens"]
                                                comp["MOTM"] = playerData["seasonStats"][compIndex]["MOTM"]
        
        with open("players.json", "w") as file:
            json.dump(teamsData, file)
    
    def saveMatches(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
        except:
            leaguesData = []

        for index, league in enumerate(leaguesData):
            if league["name"] == self.parent.tableMenu.name:
                I = index
                break

        for i, day in enumerate(self.schedule, 1): # loop through the schedule
            matches = [] # new entry for the matchDays part of the league data
            for match in day: # loop through the matches in a matchDay
                # get the data and add to the new entry
                teamHome = match[0]
                teamAway = match[1]
                time = match[2]
                matches.append({
                    "home": teamHome,
                    "away": teamAway,
                    "score": time,
                    "played": 0,
                    "homeScorers": [],
                    "awayScorers": [],
                    "homeLineup": [],
                    "awayLineup": [],
                    "injured": "",
                    "referee": "",
                    "playerOTM": "",
                    "time": time 
                })


            # Add the matches of the current matchday to the JSON data
            leaguesData[I]['matchDays'].append({
                "matchday": i,
                "matches": matches
            })

        with open('leaguesData.json', 'w') as file:
            json.dump(leaguesData, file)

    def automateMatches(self):
        startDay = None
        for index, frame in enumerate(self.activeSim): # find the first matchDay to be simulated
            if frame == 1:
                startDay = index
                break
        
        if startDay == None: # if none, return as all matchdays have been simulated
            return

        self.paused = False # update the pause variable
        self.matchesFrames[self.activeFrame].place_forget() # remove the current frame
        self.matchesFrames[startDay].place(x = 0, y = 0, anchor = "nw") # place the correct frame
        self.activeFrame = startDay # update the active frame
        self.rightArrow.configure(state = "disabled") # disable movement between frames
        self.leftArrow.configure(state = "disabled")

        try:
            with open("settings.json") as file:
                settings = json.load(file)
        except:
            settings = []

        speeds = [2000, 2500, 3000, 3500]
        speed = speeds[settings["autoSpeed"]]

        self.simulateAllMatchDays(startDay, speed) # simulate the matchDays

    def simulateAllMatchDays(self, day, speed):
        if not self.paused: # if not paused, simulation is ongoing so update the buttons
            self.autoButton.place_forget()
            self.pauseButton.place(x = 140, rely = 0.5, anchor = "center")
            self.simulateButton.configure(state = "disabled")
            self.parent.configure(state = "disabled")
            self.parent.backButton.configure(state = "disabled")
        
        if not self.paused and day < len(self.matchesFrames): # if not paused and the day is less than the total number of days, simulate the matchDay
            self.after(500, self.simMatchDay)

            self.after(speed, self.changeFrame, 1) # change the frame
            self.after(speed + 1000, self.simulateAllMatchDays, day + 1, speed) # call the function again
        else: # once over, reset the arrow
            self.rightArrow.configure(state = "normal")
            self.leftArrow.configure(state = "normal")

            self.pauseButton.place_forget() # update the buttons
            self.autoButton.place(x = 140, rely = 0.5, anchor = "center")
            self.simulateButton.configure(state = "normal")
            self.parent.configure(state = "normal")
            self.parent.backButton.configure(state = "normal")

    def pauseSim(self):
        self.pauseButton.place_forget() # update the buttons and the paused variable
        self.autoButton.place(x = 140, rely = 0.5, anchor = "center")
        self.simulateButton.configure(state = "normal")
        self.parent.configure(state = "normal")
        self.parent.backButton.configure(state = "normal")
        self.paused = True

    def getFont(self, string):
        if len(string) > 20:
            return 10
        else:
            return 13

# Class that oversees the records of the league
class RecordsMenu(ctk.CTkFrame):
    def __init__(self, parent, name, leagueMenu):
        super().__init__(parent)
        self.pack(expand = True, fill = "both")
        self.parent = leagueMenu
        self.name = name

        self.activeFrame = 0
        self.recordsFrame = []
        self.recordsFrame.append(ctk.CTkFrame(self, fg_color = GRAY))
        self.recordsFrame.append(ctk.CTkFrame(self, fg_color = GRAY))

        self.leftArrow = ctk.CTkButton(self, text = "<", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(-1)) 
        self.leftArrow.place(x = 60, y = 600, anchor = "center")

        self.rightArrow = ctk.CTkButton(self, text = ">", fg_color = ORANGE_BG, width = 50, bg_color = GRAY, height = 15, command = lambda: self.changeFrame(1))
        self.rightArrow.place(x = 310, y = 600, anchor = "center")

    def changeFrame(self, direction):
        self.recordsFrame[self.activeFrame].pack_forget() 
        if (self.activeFrame + direction == 2): 
            self.activeFrame = 0 
        else:
            self.activeFrame = self.activeFrame + direction 

            if self.activeFrame < 0:
                self.activeFrame = 1

        self.recordsFrame[self.activeFrame].pack(expand = True, fill = "both")

    def addTeamRecords(self, remove = False):
        self.recordsFrame[1].pack_forget()

        frame = self.recordsFrame[0]
        frame.pack(expand = True, fill = "both")

        frame.grid_columnconfigure(0, weight = 4)
        frame.grid_columnconfigure((1, 2, 3), weight = 1)

        for i in range(20):
            frame.grid_rowconfigure(i, weight = 1)

        if remove:
            for widget in frame.winfo_children():
                widget.destroy()

        try:
            with open("leagues.json", "r") as file:
                leagues = json.load(file)
        except:
            leagues = []

        ctk.CTkLabel(frame, text = "Record", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 0, padx = 7)
        ctk.CTkLabel(frame, text = "Value", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 1, padx = 7)
        ctk.CTkLabel(frame, text = "Team", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 2, padx = 7)
        ctk.CTkLabel(frame, text = "Season", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 3, padx = 7)

        for league in leagues:
            if league["name"] == self.name: # find the league and get the records
                records = league["teamRecords"]

                i = 0
                for record, recordData in records.items():
                    # get the data
                    value = recordData["value"]
                    team = recordData["team"]

                    ctk.CTkLabel(frame, text = record[:1].upper() + record[1:], fg_color = GRAY, text_color = "black", font = (APP_FONT, 12)).grid(row = i + 1, column = 0, sticky = "w", padx = 7)
                    ctk.CTkLabel(frame, text = value if value != 1000 else 0, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = i + 1, column = 1, padx = 7)
                    ctk.CTkLabel(frame, text = team, fg_color = GRAY, text_color = "black", font = (APP_FONT, 10)).grid(row = i + 1, column = 2, padx = 7)


                    if "season" in recordData: # this is for every record except the last as it doesnt have a season 
                        season = recordData["season"]
                        ctk.CTkLabel(frame, text = season, fg_color = GRAY, text_color = "black", font = (APP_FONT, 15)).grid(row = i + 1, column = 3, padx = 7)
                    else: # last record (most times won)
                        ctk.CTkLabel(frame, text = "N/A", fg_color = GRAY, text_color = "black", font = (APP_FONT, 12)).grid(row = i + 1, column = 3, padx = 7)

                    i += 1 # increment loop, cannot use enumerate with records.items(), dont know why

    def addIndividualRecords(self, remove = False):
        frame = self.recordsFrame[1]

        if remove:
            for widget in frame.winfo_children():
                widget.destroy()

        try:
            with open("leagues.json", "r") as file:
                leagues = json.load(file)
        except:
            leagues = []

        for league in leagues:
            if league["name"] == self.name: # find the league and get the records
                records = league["individualRecords"]

                i = 0
                yPlaces = [5, 65, 125, 185, 245, 315, 375, 435, 495]
                for record, recordData in records.items():
                    # get the data
                    player = recordData["player"]
                    value = recordData["value"]
                    team = recordData["team"]
                    season = recordData["season"]

                    ctk.CTkLabel(frame, text = record[:1].upper() + record[1:] + ":", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 5, y = yPlaces[i], anchor = "nw")
                    
                    if value != 1000:

                        if "against" in recordData:
                            against = recordData["against"]
                            ctk.CTkLabel(frame, text = player + " with " + str(value) + " for " + team, fg_color = GRAY, text_color = "black", font = (APP_FONT, 12)).place(x = 5, y = yPlaces[i] + 23, anchor = "nw")
                            ctk.CTkLabel(frame, text = "against " + against + " in season " + str(season), fg_color = GRAY, text_color = "black", font = (APP_FONT, 12), height = 10).place(x = 5, y = yPlaces[i] + 46, anchor = "nw")

                        else:
                            ctk.CTkLabel(frame, text = player + " with " + str(value) + " for " + team + " in season " + str(season), fg_color = GRAY, text_color = "black", font = (APP_FONT, 12)).place(x = 5, y = yPlaces[i] + 23, anchor = "nw")
                    else:
                        ctk.CTkLabel(frame, text = "N/A", fg_color = GRAY, text_color = "black", font = (APP_FONT, 12)).place(x = 5, y = yPlaces[i] + 23, anchor = "nw")

                    i += 1 

# Class that oversees the past seasons of the league
class SeasonsMenu(ctk.CTkScrollableFrame):
    def __init__(self, parent, leagueMenu, name):
        super().__init__(parent, fg_color = GRAY, scrollbar_button_color = DARK_GRAY)
        self.parent = parent
        self.leagueMenu = leagueMenu
        self.name = name
        self.season = 0
        self.graphsMenu = None
        self.currentFrame = "Table"

        self.pack(expand = True, fill = "both")

        self.tableFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 570)
        self.tableFrame.grid_propagate(False)

        self.tableFrame.grid_columnconfigure(0, weight = 3)
        self.tableFrame.grid_columnconfigure(1, weight = 6)
        self.tableFrame.grid_columnconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight = 1)
        self.tableFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21), weight = 1)

        self.graphFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 540)
        self.graphTitleFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 40)
        self.graphTitle = ctk.CTkLabel(self.graphTitleFrame, text = "Positions", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 20))
        self.graphTitle.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.statsFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 570)

        self.defaultButtonsFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 65)
        self.graphsButton = ctk.CTkButton(self.defaultButtonsFrame, text = "Graphs", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeToGraphs())
        self.graphsButton.place(relx = 0.2, rely = 0.5, anchor = "center")
        self.statsButtton = ctk.CTkButton(self.defaultButtonsFrame, text = "Stats", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeToStats())
        self.statsButtton.place(relx = 0.4, rely = 0.5, anchor = "center")
        self.tableButton = ctk.CTkButton(self.defaultButtonsFrame, text = "Table", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeToTable())
        self.tableButton.place(relx = 0.6, rely = 0.5, anchor = "center")
        self.backButton = ctk.CTkButton(self.defaultButtonsFrame, text = "Back", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = self.goBack)
        self.backButton.place(relx = 0.8, rely = 0.5, anchor = "center")

        self.graphButtonsFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 65)
        self.changeGraphButton = ctk.CTkButton(self.graphButtonsFrame, text = "Points", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15)
        self.changeGraphButton.place(relx = 0.25, rely = 0.5, anchor = "center")
        self.changeGraphButton.configure(command = lambda: self.graphsMenu.changeGraph(self.graphTitle, self.changeGraphButton))
        self.reset = ctk.CTkButton(self.graphButtonsFrame, text = "Reset", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.graphsMenu.reset())
        self.reset.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.backButton = ctk.CTkButton(self.graphButtonsFrame, text = "Back", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.goBackFromGraphs())
        self.backButton.place(relx = 0.75, rely = 0.5, anchor = "center")

    def importSeasons(self):
        try:
            with open("seasonsData.json", "r") as file:
                seasonsData = json.load(file)
        except:
            seasonsData = []

        for league in seasonsData:
            if league["name"] == self.name:
                currLeague = league
                break
        
        for i, winner in enumerate(currLeague["winners"], 1):
            self.addNewSeason(winner, i, True)

    def addNewSeason(self, winner, season = 0, imported = False):
        frame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 350, height = 100)
        frame.pack(expand = True, fill = "both", pady = (0, 5))

        ctk.CTkLabel(frame, text = "Winner:", font = (APP_FONT, 18)).place(x = 10, y = 5, anchor = "nw")
        ctk.CTkLabel(frame, text = "Season", font = (APP_FONT, 18)).place(x = 290, y = 20, anchor = "center")

        src = Image.open("SavedImages/Teams/" + winner + ".png")
        logo = ctk.CTkImage(src, None, (50, 50))
        ctk.CTkLabel(frame, text = "", image = logo).place(x = 10, y = 35, anchor = "nw")
        ctk.CTkLabel(frame, text = winner, font = (APP_FONT_BOLD, self.getFont(winner))).place(x = 80, y = 45, anchor = "nw")

        try:
            with open("leagues.json",  "r") as file:
                leagues = json.load(file)
        except:
            leagues = []

        if not imported:
            for league in leagues:
                if league["name"] == self.name:
                    season = league["seasons"]
                    break
        
        ctk.CTkLabel(frame, text = season, font = (APP_FONT, 35)).place(x = 290, y = 60, anchor = "center")

        for widget in frame.winfo_children():
            widget.bind("<Enter> <Button-1>", lambda event: self.openMenu(event, season))

        frame.bind("<Enter> <Button-1>", lambda event: self.openMenu(event, season))

    def openMenu(self, event, season):
        self.pack_forget()
        self.season = season

        for widget in self.tableFrame.winfo_children():
            widget.destroy()
        
        for widget in self.graphFrame.winfo_children():
            widget.destroy()

        for widget in self.statsFrame.winfo_children():
            widget.destroy()

        self.tableFrame.pack(expand = True, fill = "both", pady = (0,5))
        self.defaultButtonsFrame.pack(expand = True, fill = "both")

        self.tableButton.configure(state = "disabled")
        self.statsButtton.configure(state = "normal")

        ctk.CTkLabel(self.tableFrame, text = "#", fg_color = GRAY, text_color = "black").grid(row = 0, column = 0)
        ctk.CTkLabel(self.tableFrame, text = "Team", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 2, sticky = "w")
        ctk.CTkLabel(self.tableFrame, text = "GP", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 3)
        ctk.CTkLabel(self.tableFrame, text = "W", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 4)
        ctk.CTkLabel(self.tableFrame, text = "D", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 5)
        ctk.CTkLabel(self.tableFrame, text = "L", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 6)
        ctk.CTkLabel(self.tableFrame, text = "GF", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 7)
        ctk.CTkLabel(self.tableFrame, text = "GA", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 8)
        ctk.CTkLabel(self.tableFrame, text = "GD", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 9)
        ctk.CTkLabel(self.tableFrame, text = "P", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).grid(row = 0, column = 10)

        try:
            with open("seasonsData.json", "r") as file:
                seasonsData = json.load(file)
        except:
            seasonsData = []

        for league in seasonsData:
            if league["name"] == self.name:
                currLeague = league
                break

        for table in currLeague["tables"]:
            if table["season"] == season:
                data = table["table"]
                break
        
        positionsData = currLeague["positions"][season - 1]["positions"]
        pointsData = currLeague["points"][season - 1]["points"]

        dictEntries = ["gp", "w", "d", "l", "gf", "ga", "gd", "p"]
        for i, team in enumerate(data):
            ctk.CTkLabel(self.tableFrame, text = i + 1, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).grid(row = i + 1, column = 0)

            src = Image.open("SavedImages/Teams/" + team["team"] + ".png")
            logo = ctk.CTkImage(src, None, (20, 20))
            logoLabel = ctk.CTkLabel(self.tableFrame, text = "", image = logo, fg_color = GRAY)
            logoLabel.grid(row = i + 1, column = 1)

            nameLabel = ctk.CTkLabel(self.tableFrame, text = team["team"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 12))
            nameLabel.grid(row = i + 1, column = 2, sticky = "w")

            for j in range(8):
                label = ctk.CTkLabel(self.tableFrame, text = team[dictEntries[j]], fg_color = GRAY, text_color = "black", font = (APP_FONT, 15))
                label.grid(row = i + 1, column = j + 3)

        self.graphsMenu = GraphsMenu(self.graphFrame, self.leagueMenu.numTeams, self.name, self.leagueMenu)
        self.graphsMenu.addGraph(False, True, positionsData, pointsData)

        titles = ["Top Scorer", "Top Assister", "Best Average Rating", "Most Clean Sheets", "Most Penalties", "Most Player of the Match"]
        recordTitles = ["topScorer", "topAssister", "topAverageRating", "topCleanSheet", "topPen", "topPOTM"]

        for i in range(len(titles)):
            data = currLeague[recordTitles[i]][season - 1][recordTitles[i]]

            if i == 0:
                padding = 5
            else:
                padding = (0,5)

            packFrame = ctk.CTkFrame(self.statsFrame, fg_color = GRAY, height = 90, border_color = DARK_GRAY, border_width = 2)
            packFrame.pack(expand = True, fill = "both", pady = padding, padx = 5)

            ctk.CTkLabel(packFrame, text = titles[i], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 10, rely = 0.03, anchor = "nw")

            playerName = data["name"]
            teamName = data["team"]
            playerImage = self.findPlayerImage(playerName, teamName)
            ctk.CTkLabel(packFrame, text = "", image = playerImage, fg_color = GRAY).place(x = 40, rely = 0.6, anchor = "center")

            ctk.CTkLabel(packFrame, text = playerName, fg_color = GRAY, text_color = "black", font = (APP_FONT, 15)).place(x = 75, rely = 0.3, anchor = "nw")

            src = "SavedImages/Teams/" + teamName + ".png"
            img = Image.open(src)
            ctk.CTkLabel(packFrame, text = "", image = ctk.CTkImage(img, None, (20, 20)), fg_color = GRAY).place(x = 75, rely = 0.58, anchor = "nw")
            ctk.CTkLabel(packFrame, text = teamName, fg_color = GRAY, text_color = "black", font = (APP_FONT, 15)).place(x = 105, rely = 0.58, anchor = "nw")

            stat = data["stat"]

            if isinstance(stat, float): # only for ratings, a 9.2 becomes 9.20
                stat = f"{stat:.2f}"

            ctk.CTkLabel(packFrame, text = str(stat), fg_color = GRAY, text_color = "black", font = (APP_FONT, 25)).place(x = 310, rely = 0.5, anchor = "center")

    def findPlayerImage(self, playerName, teamName):
        try:
            with open("players.json", "r") as file:
                players = json.load(file)
        except:
            players = []

        for team in players:
            if team["name"] == teamName:
                for i, player in enumerate(team["players"], 1):
                    if player["name"] == playerName:
                        playerIndex = i
        
        # check if the player has an image
        imagePath = f"SavedImages/Players/{teamName}_{playerIndex}.png"
        if not os.path.exists(imagePath):
            imagePath = "Images/user.png"

        img = Image.open(imagePath)
        playerImage = ctk.CTkImage(img, None, (50, 50))

        return playerImage

    def changeToGraphs(self):
        self.tableFrame.pack_forget()
        self.statsFrame.pack_forget()
        self.defaultButtonsFrame.pack_forget()

        self.graphTitleFrame.pack(expand = True, fill = "both")
        self.graphFrame.pack(expand = True, fill = "both", pady = 5)
        self.graphButtonsFrame.pack(expand = True, fill = "both")

    def goBackFromGraphs(self):
        self.graphTitleFrame.pack_forget()
        self.graphFrame.pack_forget()
        self.graphButtonsFrame.pack_forget()

        if self.currentFrame == "Table":
            self.tableFrame.pack(expand = True, fill = "both", pady = (0,5))
        else:
            self.statsFrame.pack(expand = True, fill = "both", pady = (0,5))

        self.defaultButtonsFrame.pack(expand = True, fill = "both")

    def changeToStats(self):
        self.tableFrame.pack_forget()
        self.defaultButtonsFrame.pack_forget()

        self.statsFrame.pack(expand = True, fill = "both", pady = (0,5))
        self.defaultButtonsFrame.pack(expand = True, fill = "both")

        self.currentFrame = "Stats"
        self.tableButton.configure(state = "normal")
        self.statsButtton.configure(state = "disabled")

    def changeToTable(self):
        self.statsFrame.pack_forget()
        self.defaultButtonsFrame.pack_forget()

        self.tableFrame.pack(expand = True, fill = "both", pady = (0,5))
        self.defaultButtonsFrame.pack(expand = True, fill = "both")

        self.currentFrame = "Table"
        self.tableButton.configure(state = "disabled")
        self.statsButtton.configure(state = "normal")

    def goBack(self):
        self.tableFrame.pack_forget()
        self.statsFrame.pack_forget()
        self.defaultButtonsFrame.pack_forget()
        self.pack(expand = True, fill = "both")

    def getFont(self, str):
        if len(str) > 25:
            return 15
        elif len(str) > 10:
            return 18
        elif len(str) > 15:
            return 20
        else:
            return 22

# Class that oversees the graphs for a season
class GraphsMenu(ctk.CTkFrame):
    def __init__(self, parent, numTeams, name, leagueMenu):
        super().__init__(parent, fg_color = APP_BACKGROUND)
        self.numTeams = numTeams
        self.name = name
        self.parent = leagueMenu
        self.imgs = []  # Create a list to store all the images
        self.graph = "positions"

        self.canvasWidth = 433
        self.canvasHeight = 640 # before was 620
        self.rows = self.numTeams - 1

        self.titleFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 40)
        self.titleFrame.pack(expand = True, fill = "both")
        self.canvasFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 540)
        self.canvasFrame.pack(expand = True, fill = "both", pady = 5)
        self.buttonsFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 65)
        self.buttonsFrame.pack(expand = True, fill = "both")

        self.canvasParent = self.canvasFrame
        self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
        self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.resetButton = ctk.CTkButton(self.buttonsFrame, text = "Reset", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, state = "disabled", command = lambda: self.reset())
        self.resetButton.place(relx = 0.66, rely = 0.5, anchor = "center")

        self.changeButton = ctk.CTkButton(self.buttonsFrame, text = "Points", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, state = "disabled", command = lambda: self.changeGraph())
        self.changeButton.place(relx = 0.33, rely = 0.5, anchor = "center")

        self.titleLabel = ctk.CTkLabel(self.titleFrame, text = "Positions", font = (APP_FONT_BOLD, 23), text_color = "black")
        self.titleLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

    def reset(self):
        self.canvas.delete("all")

        if self.graph == "positions":
            first = list(self.positions.keys())[0]
            length = len(self.positions[first])

            self.rows = self.numTeams - 1

            self.drawGrid(length - 1)

            for i, team in enumerate(self.positions):
                src = "SavedImages/Teams/" + team + ".png"
                self.addPoints(self.positions[team], src, length - 1, i)
        
        else:
            first = list(self.points.keys())[0]
            length = len(self.points[first])
            mostPoints = max(x[-1] for x in self.points.values())
            self.rows = int(mostPoints)

            self.drawGrid(length - 1)

            for i, team in enumerate(self.points):
                src = "SavedImages/Teams/" + team + ".png"
                self.addPoints(self.points[team], src, length - 1, i)

    def changeGraph(self, titleLabel = None, buttonLabel = None):
        if self.graph == "positions":
            self.graph = "points"
            self.changeButton.configure(text = "Positions")
            self.titleLabel.configure(text = "Points")
            self.addGraph(season = self.season, positions = self.positions, points = self.points)

            if titleLabel is not None:
                titleLabel.configure(text = "Points")
                buttonLabel.configure(text = "Positions")
        else:
            self.graph = "positions"
            self.changeButton.configure(text = "Points")
            self.titleLabel.configure(text = "Positions")
            self.addGraph(season = self.season, positions = self.positions, points = self.points)

            if titleLabel is not None:
                titleLabel.configure(text = "Positions")
                buttonLabel.configure(text = "Points")

    def addGraph(self, first = False, season = False, positions = None, points = None):
        self.season = season

        if self.season:
            self.canvasParent = self.parent.seasonsMenu.graphFrame
            self.positions = positions
            self.points = points
        else:
            self.canvasParent = self.canvasFrame
            self.pack(expand = True, fill = "both")
            self.positions = self.parent.matchesMenu.positions
            self.points = self.parent.matchesMenu.points
            
        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)
        except:
            data = []

        if first:
            for league in data:
                if league["name"] == self.name:
                    if league["teams"] != []:
                        first = list(self.positions.keys())[0]
                        lastMatchDay = len(self.positions[first])
                    else:
                        lastMatchDay = 0

        if not first:
            first = list(self.positions.keys())[0]
            lastMatchDay = len(self.positions[first])

        if lastMatchDay >= 2:
            if self.graph == "positions":
                self.rows = self.numTeams - 1
                
                self.canvas.pack_forget()
                self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
                self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")
                self.drawGrid(lastMatchDay - 1)

                for i, team in enumerate(self.positions):
                    src = "SavedImages/Teams/" + team + ".png"
                    self.addPoints(self.positions[team], src, lastMatchDay - 1, i)
            else:
                mostPoints = max(x[-1] for x in self.points.values())
                self.rows = int(mostPoints)

                self.canvas.pack_forget()
                self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
                self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")
                self.drawGrid(lastMatchDay - 1)

                for i, team in enumerate(self.points):
                    src = "SavedImages/Teams/" + team + ".png"
                    self.addPoints(self.points[team], src, lastMatchDay - 1, i)
        else: # default empty graph
            if self.graph == "positions":
                self.rows = self.numTeams - 1
            else:
                self.rows = 3

            self.canvas.pack_forget()
            self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
            self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")
            self.drawGrid(1)

    def drawGrid(self, columns):
        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / columns  # Subtract 50 to add a space of 20 pixels on the left and 30 on the right
        cellHeight = (self.canvasHeight - 40) / self.rows  # Subtract 40 to add a space of 20 pixels on the top and bottom

       # Draw vertical lines
        for i in range(columns):
            x = i * cellWidth + 20  # Add 20 to move the grid 20 pixels to the right
            self.canvas.create_line(x, 20, x, self.canvasHeight - 20, fill= DARK_GRAY, dash = (4, 2))  # Add 20 to move the lines down 20 pixels and subtract 20 to move them up 20 pixels at the bottom

            # Add matchDays at the bottom of each column
            if i == 0 or (i + 1) % 5 == 0:
                self.canvas.create_text(x, self.canvasHeight - 12, text = str(i + 1), anchor = "n")  # Subtract 10 to move the text up 10 pixels at the bottom

        # Draw the last vertical line
        self.canvas.create_line(self.canvasWidth - 30, 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = DARK_GRAY, dash = (4, 2)) # Subtract 30 to move the lines 30 pixels to the left and add 20 to move them down 20 pixels and subtract 20 to move them up 20 pixels at the bottom

        # Add the last matchDay at the bottom
        self.canvas.create_text(self.canvasWidth - 30, self.canvasHeight - 12, text = str(columns + 1), anchor = "n")  # Subtract 30 to move the text 30 pixels to the left and subtract 10 to move it up 10 pixels at the bottom

        # Draw horizontal lines
        for i in range(self.rows):
            y = i * cellHeight + 20  # Add 20 to move the lines down 20 pixels
            self.canvas.create_line(20, y, self.canvasWidth - 30, y, fill = DARK_GRAY, dash = (4, 2))  # Add 20 to move the grid 20 pixels to the right and subtract 30 to move it 30 pixels to the left

            # Add row number at the top of the row
            if self.graph == "positions":
                self.canvas.create_text(10, y - 8, text = str(i + 1), anchor = "n")  # Move the text 10 pixels to the left
            else:
                if i == 0 or (self.rows - i) % 5 == 0:
                    self.canvas.create_text(10, y - 8, text = str(self.rows - i), anchor = "n")

        # Draw the last horizontal line
        self.canvas.create_line(20, self.canvasHeight - 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = DARK_GRAY, dash = (4, 2))  # Add 20 to move the grid 20 pixels to the right and subtract 30 to move it 30 pixels to the left and subtract 20 to move it up 20 pixels at the bottom

        # Add the last row number
        if self.graph == "positions":
            self.canvas.create_text(10, self.canvasHeight - 28, text = self.numTeams, anchor = "n")  # Move the text 10 pixels to the left and subtract 20 to move it up 20 pixels at the bottom
        else:
            self.canvas.create_text(10, self.canvasHeight - 28, text = "0", anchor = "n")

    def addPoints(self, positions, logo, columns, index, first = True, delete = False):

        if columns + 1 >= 2:
            self.resetButton.configure(state = "normal")
            self.changeButton.configure(state = "normal")

        if delete:
            self.canvas.delete("non_image")
        elif not first and not delete:
            self.canvas.delete("line" + str(index))

        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / columns
        cellHeight = (self.canvasHeight - 40) / self.rows

        # Store the coordinates of each point
        points = []

        # Draw a point on each row
        for i, position in enumerate(positions):
            x = 20 + i * cellWidth  # Place the point on the grid line

            if self.graph == "positions":
                y = 20 + (position - 1) * cellHeight  # Place the point on the grid line
            else:
                y = 20 + (self.rows - position) * cellHeight

            # Add the coordinates of the point to the list
            points.append(x)
            points.append(y)

        src = Image.open(logo)
        src = src.resize((20, 20))
        img = ImageTk.PhotoImage(src)
        self.imgs.append(img)  # Add the image to the list

        # Add the logo 10 pixels after the row
        imageID = self.canvas.create_image(self.canvasWidth - 10, y, image = self.imgs[index], tags = "image" + str(index))
        if (not delete and first) or (not delete and not first):
            self.canvas.tag_bind("image" + str(index), "<Enter> <Button-1>", lambda event, positions = positions, logo = logo, columns = columns, index = index: self.addPoints(positions, logo, columns, index, False, True))
        elif delete:
            self.canvas.tag_bind("image" + str(index), "<Enter> <Button-1>", lambda event, positions = positions, logo = logo, columns = columns, index = index: self.addPoints(positions, logo, columns, index, False, False))

        # Draw a line connecting all points with a wider line
        if not delete and first:
            self.canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "non_image")
        elif not first and delete:
            self.canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "line" + str(index))

# Class that oversees the stats for a season
class StatsMenu(ctk.CTkFrame):
    def __init__(self, parent, leagueMenu, leagueName):
        super().__init__(parent, fg_color = APP_BACKGROUND)
        self.pack(expand = True, fill = "both")
        self.parent = parent
        self.leagueMenu = leagueMenu
        self.name = leagueName

        self.statsFrames = []
        self.statsTitles = ["Top Scorer", "Top Assister", "Best Average Rating", "Most Clean Sheets", "Most Penalties scored", "Most Man of the Match"]
        self.activeFrame = 0
        self.statsNum = 6 # number of stats to show

    def createFrames(self):
        for _ in range(self.statsNum):
            frame = ctk.CTkFrame(self, fg_color = GRAY, height = 537, width = 368)
            self.statsFrames.append(frame)

        self.statsFrames[0].place(x = 0, y = 45, anchor = "nw")

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 40.5, width = 368)
        self.buttonsFrame.place(x = 0, y = 588, anchor = "nw")

        self.titleFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 40, width = 368)
        self.titleFrame.place(x = 0, y = 0, anchor = "nw")

        self.leftArrow = ctk.CTkButton(self.buttonsFrame, text = "<", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(-1)) # go back a matchday
        self.leftArrow.place(relx = 0.25, rely = 0.5, anchor = "center")

        self.rightArrow = ctk.CTkButton(self.buttonsFrame, text = ">", fg_color = ORANGE_BG, width = 50, bg_color = GRAY, height = 15, command = lambda: self.changeFrame(1)) # go forward a matchday
        self.rightArrow.place(relx = 0.75, rely = 0.5, anchor = "center")

        self.statsTitle = ctk.CTkLabel(self.titleFrame, text = "Top Scorer", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 20))
        self.statsTitle.place(relx = 0.5, rely = 0.5, anchor = "center")

    def changeFrame(self, direction):
        self.statsFrames[self.activeFrame].place_forget() 
        if self.activeFrame + direction == self.statsNum: 
            self.activeFrame = 0 
        else:
            self.activeFrame = self.activeFrame + direction

            if self.activeFrame < 0:
                self.activeFrame = self.statsNum - 1

        self.statsFrames[self.activeFrame].place(x = 0, y = 45, anchor = "nw")
        self.statsTitle.configure(text = self.statsTitles[self.activeFrame])

    def importStats(self):
        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)
        except:
            data = []

        self.createFrames()

        for league in data:
            if league["name"] == self.name:
                topScorers = league["topScorer"]
                topAssisters = league["topAssister"]
                topAverageRatings = league["topAverageRating"]
                topCleanSheets = league["topCleanSheet"]
                topPens = league["topPen"]
                topPOTM = league["topPOTM"]
                break

        self.updateStats(topScorers, topAssisters, topAverageRatings, topCleanSheets, topPens, topPOTM)

    def updateStats(self, topScorers, topAssisters, topAverageRatings, topCleanSheets, topPens, topMOTM):

        if topScorers == []:
            return

        dataList = [topScorers, topAssisters, topAverageRatings, topCleanSheets, topPens, topMOTM]
        backgroundColor = GRAY
        borderColor = DARK_GRAY
        borderWidth = 2

        for i in range(self.statsNum):
            frame = self.statsFrames[i]

            for widget in frame.winfo_children():
                widget.destroy()

            height = 71
            yPlaces = [5, 81, 157, 233, 309, 385, 461]
            for j in range(len(dataList[i])):
                packFrame = ctk.CTkFrame(frame, fg_color = backgroundColor, height = height, width = 358, border_width = borderWidth, border_color = borderColor)
                packFrame.place(x = 5, y = yPlaces[j], anchor = "nw")

                ctk.CTkLabel(packFrame, text = str(j + 1) + ".", fg_color = backgroundColor, text_color = "black", font = (APP_FONT, 15)).place(x = 20, rely = 0.5, anchor = "center")
        
                playerName = dataList[i][j]["name"]
                teamName = dataList[i][j]["team"]
                playerImage = self.findPlayerImage(playerName, teamName)
                ctk.CTkLabel(packFrame, text = "", image = playerImage, fg_color = backgroundColor).place(x = 60, rely = 0.5, anchor = "center")

                ctk.CTkLabel(packFrame, text = playerName, fg_color = backgroundColor, text_color = "black", font = (APP_FONT, 15)).place(x = 95, rely = 0.15, anchor = "nw")

                src = "SavedImages/Teams/" + teamName + ".png"
                img = Image.open(src)
                ctk.CTkLabel(packFrame, text = "", image = ctk.CTkImage(img, None, (20, 20)), fg_color = backgroundColor).place(x = 95, rely = 0.48, anchor = "nw")
                ctk.CTkLabel(packFrame, text = teamName, fg_color = backgroundColor, text_color = "black", font = (APP_FONT, 15)).place(x = 125, rely = 0.48, anchor = "nw")

                stat = dataList[i][j]["stat"]

                if isinstance(stat, float): # only for ratings, a 9.2 becomes 9.20
                    stat = f"{stat:.2f}"

                ctk.CTkLabel(packFrame, text = str(stat), fg_color = backgroundColor, text_color = "black", font = (APP_FONT, 25)).place(x = 310, rely = 0.5, anchor = "center")

    def findPlayerImage(self, playerName, teamName):
        try:
            with open("players.json", "r") as file:
                players = json.load(file)
        except:
            players = []

        for team in players:
            if team["name"] == teamName:
                for i, player in enumerate(team["players"], 1):
                    if player["name"] == playerName:
                        playerIndex = i
        
        # check if the player has an image
        imagePath = f"SavedImages/Players/{teamName}_{playerIndex}.png"
        if not os.path.exists(imagePath):
            imagePath = "Images/user.png"

        img = Image.open(imagePath)
        playerImage = ctk.CTkImage(img, None, (50, 50))

        return playerImage


