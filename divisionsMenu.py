import customtkinter as ctk
from settings import *
import json, random, re, os, heapq
from PIL import Image, ImageTk
from faker import Faker

class DivisionsMenu(ctk.CTkTabview):
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
        self.numPromotions = numPromotions
        self.teamsMenu = teamsMenu
        self.mainMenu = mainMenu
        self.name = name
        self.root = rootWindow

        self.tableMenu = TableMenu(self.tab("Table"), self, self.name, self.numTeams, self.divisions, self.numPromotions, self.mainMenu)
        self.matchesMenu = MatchesMenu(self.tab("Matches"), self, self.numTeams, self.divisions)
        self.statsMenu = StatsMenu(self.tab("Stats"), self, name)
        self.graphsMenu = GraphsMenu(self.tab("Graphs"), self.numTeams, self.name, self)
        self.recordsMenu = RecordsMenu(self.tab("Records"), self, self.name)
        self.seasonsMenu = SeasonsMenu(self.tab("Seasons"), self, name)

        self._segmented_button.grid(sticky = "w")

        self.backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBack())
        self.backButton.place(x = 378, y = 0, anchor = "ne")

        self.newSeasonButton = ctk.CTkButton(self, text = "New", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", width = 34, height = 15, corner_radius = 5, state = "disabled", command = lambda: self.newSeason())
        self.newSeasonButton.place(x = 378, y = 20, anchor = "ne")

    def goBack(self):
        self.matchesMenu.saveTable()
        self.mainMenu.pack(expand = True, fill = "both")

        if(hasattr(self.tableMenu, "selectedVar")):
            self.tableMenu.selectedTeams = []
            self.tableMenu.selectedVar.set(0)
            self.tableMenu.selectionFrame.place_forget()
            self.tableMenu.createTableFrame.place_forget()

        for frame in self.tableMenu.divFrames:
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.place(x = 185, y = 280, anchor = "center")

        self.pack_forget()

    def importData(self, leagueData, league):

        self.tableMenu.numTeams = league["teams"]
        self.tableMenu.name = leagueData["name"]
        self.tableMenu.divisions = league["divisions"]
        self.tableMenu.numPromotions = league["promoted"]

        index = -1
        for i, division in enumerate(leagueData["divisions"]):
            if division["teams"] == []:
                index = i - 1
                break

        if index == -1:
            index = len(leagueData["divisions"]) - 1

        self.tableMenu.addTeams(leagueData, index, True)

    def newSeason(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
            
            with open("teams.json", "r") as file:
                teamsBasic = json.load(file)

            with open("leagues.json") as file:
                leagues = json.load(file)

            with open("players.json", "r") as file:
                teams = json.load(file)
            
            with open("seasonsData.json") as file:
                seasonsData = json.load(file)

            with open("settings.json") as file:
                settings = json.load(file)
        except:
            leaguesData = []
            teamsBasic = []
            leagues = []
            seasonsData = []
            teams = []
            settings = []

        winner = self.tableMenu.tableTeams[0][0][0]

        hattrickCounts = {}
        goalsWithoutPenaltiesCount = {}
        mostGoalsInGame = {"name": None, "goals": 0, "against": None}

        for league in leaguesData: # finding the league and updating the matches and individual records
            if league["name"] == self.name:
                currLeague = league

                for matchday in currLeague["divisions"][0]['matchDays']: # before resseting the matchDays, find the individual records only for the first division
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
                            
                        #         if scorer["assister"] != "none":
                        #             if scorer['assister'] not in assistsCounts:
                        #                 assistsCounts[scorer['assister']] = 1
                        #             else:
                        #                 assistsCounts[scorer['assister']] += 1

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

                seasonTopScorer = currLeague["divisions"][0]["topScorer"][0]
                currLeague["divisions"][0]["topScorer"] = []
                seasonTopAssister = currLeague["divisions"][0]["topAssister"][0]
                currLeague["divisions"][0]["topAssister"] = []
                seasonTopAverageRating = currLeague["divisions"][0]["topAverageRating"][0]
                currLeague["divisions"][0]["topAverageRating"] = []
                seasonTopCleanSheets = currLeague["divisions"][0]["topCleanSheet"][0]
                currLeague["divisions"][0]["topCleanSheet"] = []
                seasonTopPens = currLeague["divisions"][0]["topPen"][0]
                currLeague["divisions"][0]["topPen"] = []
                seasonTopPOTM = currLeague["divisions"][0]["topPOTM"][0]
                currLeague["divisions"][0]["topPOTM"] = []

                break

        mostTimesWon = 0
        mostTimesTeam = ""
        for divIndex, div in enumerate(currLeague["divisions"]): # team, player records and level changes
            div["matchDays"] = []
            for team in div["teams"]: # team records
                teamRecords = team["seasonRecords"]
            
                # update the team's records for that league, only if they are in the first division
                if divIndex == 0:
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

            if settings["levelChange"] == 1: # level changes
                # update the team's level according to their finising position and the list levels [200, 198, 196, ..., 2]
                levels = list(range(200, 1, -2))
                lastIndex = 0
                for i, div in enumerate(self.tableMenu.tableTeams):
                    for j, team in enumerate(div):
                        for teamData in teams:
                            if team[0].cget("text") == teamData["name"]:
                                teamData["level"] = levels[j + lastIndex]
                    lastIndex += j + 1
                
                changedLevels = True
            else:
                changedLevels = False

            with open("teams.json", "w") as file:
                json.dump(teamsBasic, file)

            for team in teams: # player records
                if team["name"] in [team[0].cget("text") for team in self.tableMenu.tableTeams[divIndex]]:
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
                        
                        player["matches"] = [match for match in player["matches"] if match["compName"] != self.name]

            with open("players.json", "w") as file:
                json.dump(teams, file)
        
        ## change teams in leaguesData.json based on promotions and relegations
        promotedTeams = [[] for _ in range(self.divisions - 1)]
        relegatedTeams = [[] for _ in range(self.divisions - 1)]

        for i, div in enumerate(self.tableMenu.tableTeams[1:]): # find promotedTeamns
            for j, teamLabels in enumerate(div):

                for division in currLeague["divisions"]:
                    for team in division["teams"]:
                        if team["name"] == teamLabels[0].cget("text"):
                            promotedTeams[i].append(team)

                if j == self.numPromotions - 1:
                    break

        for i, div in enumerate(self.tableMenu.tableTeams[:-1]): # find relegatedTeams
            for j, teamLabels in enumerate(reversed(div)):

                for division in currLeague["divisions"]:
                    for team in division["teams"]:
                        if team["name"] == teamLabels[0].cget("text"):
                            relegatedTeams[i].append(team)

                if j == self.numPromotions - 1:
                    break

        for i, div in enumerate(currLeague["divisions"]): # change the teams in the leagueData.json file
            teams = div["teams"]

            if i == 0:
                for team in promotedTeams[i]:
                    teams.append(team)
                for team in relegatedTeams[i]:
                    teams.remove(team)
            elif i >= 1 and i < self.divisions - 1:
                for team in promotedTeams[i - 1]:
                    teams.remove(team)
                for team in promotedTeams[i]:
                    teams.append(team)
                for team in relegatedTeams[i - 1]:
                    teams.append(team)
                for team in relegatedTeams[i]:
                    teams.remove(team)
            else:
                for team in promotedTeams[i - 1]:
                    teams.remove(team)
                for team in relegatedTeams[i - 1]:
                    teams.append(team)

        with open("leaguesData.json", "w") as file:
            json.dump(leaguesData, file)

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

        for league in seasonsData:
            if league["name"] == self.name:

                league["winners"].append(winner.cget("text"))

                newEntry = {
                    "season": currSeason,
                    "table": []
                }

                positionsEntry = {
                    "season": currSeason,
                    "positions": self.matchesMenu.positions["1"]
                }

                pointsEntry = {
                    "season": currSeason,
                    "points": self.matchesMenu.points["1"]
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

                for team in self.tableMenu.tableTeams[0]:
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

        for div in self.tableMenu.tableTeams:
            for teamLabels in div:
                for label in teamLabels:
                    if label.cget("text").isdigit() or self.isNeg(label.cget("text")):
                        label.configure(text = "0")

        ## change table labels based on promotions and relegations
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
        except:
            leaguesData = []

        self.newSeasonButton.configure(state = "disabled")
        self.matchesMenu.destroy()
        self.matchesMenu = MatchesMenu(self.tab("Matches"), self, self.numTeams, self.divisions)
        self.matchesMenu.sortTable(False)

        for league in leaguesData:
            if league["name"] == self.name:
                self.tableMenu.destroy()
                self.tableMenu = TableMenu(self.tab("Table"), self, self.name, self.numTeams, self.divisions, self.numPromotions, self.mainMenu)
                self.tableMenu.addTeams(league, self.divisions - 1, True)

        self.graphsMenu.destroy()
        self.graphsMenu = GraphsMenu(self.tab("Graphs"), self.numTeams, self.name, self)
        self.graphsMenu.addGraph(True, False)

        self.statsMenu.destroy()
        self.statsMenu = StatsMenu(self.tab("Stats"), self, self.name)
        self.statsMenu.importStats()

        self.seasonsMenu.pack_forget()
        self.seasonsMenu = SeasonsMenu(self.tab("Seasons"), self, self.name)
        self.seasonsMenu.importSeasons()

        if changedLevels:   
            self.teamsMenu.updateLevels() # call the updateLevels function in menu.py which will change the level labels in the teams menu

        self.recordsMenu.addTeamRecords(True) # update the league's records (True says that they are replacing old ones)
        self.recordsMenu.addIndividualRecords(True)
    
    def getData(self, index, most = True):
        data = self.tableMenu.tableTeams[0]

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
        if str.startswith('-') and str[1:].isdigit():
            return True
        return False

class TableMenu(ctk.CTkFrame):
    def __init__(self, parent, divisionsMenu, name, numTeams, divisions, numPromotions, mainMenu):
        super().__init__(parent)
        self.pack(expand = True, fill = "both") 

        self.parent = divisionsMenu
        self.name = name
        self.numTeams = numTeams
        self.divisions = divisions
        self.numPromotions = numPromotions
        self.mainMenu = mainMenu
        self.addFrames = [0] * self.divisions
        self.addFrames[0] = 1
        self.activeFrame = 0 # start at frame 0 to add teams
        self.divFrames = [] * self.divisions
        self.finishedTables = [0] * self.divisions

        self.tableTeams = []
        self.tableLogos = []
        self.selectedTeams = []
        
        self.createFrames()

        self.leftArrow = ctk.CTkButton(self, text = "<", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(-1)) # go back a matchday
        self.leftArrow.place(x = 60, y = 600, anchor = "center")

        self.rightArrow = ctk.CTkButton(self, text = ">", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(1)) # go forward a matchday
        self.rightArrow.place(x = 310, y = 600, anchor = "center")

        self.divLabel = ctk.CTkLabel(self, text = "Division 1", fg_color = ORANGE_BG, font = (APP_FONT_BOLD, 15), corner_radius = 5, width = 30, bg_color = GRAY)
        self.divLabel.place(x = 185, y = 600, anchor = "center")

    def changeFrame(self, direction):
        self.divFrames[self.activeFrame].pack_forget() # remove it
        if (self.activeFrame + direction == self.divisions): 
            self.activeFrame = 0 
            text = "Division 1"
        elif (self.activeFrame + direction == -1):
            self.activeFrame = self.divisions - 1
            text = "Division " + str(self.divisions)
        else:
            self.activeFrame = self.activeFrame + direction 
            text = "Division " + str(self.activeFrame + 1)

        self.divFrames[self.activeFrame].pack(expand = True, fill = "both") # add it back
        self.divLabel.configure(text = text)

    def createFrames(self):

        try:
            with open("teams.json", "r") as file:
                self.teams = json.load(file)
        except:
            self.teams = []

        for i in range(self.divisions):
            frame = ctk.CTkFrame(self)
            addTeamsButton = ctk.CTkButton(frame, text = "Add teams for division " + str(i + 1), fg_color = ORANGE_BG)
            addTeamsButton.configure(command = lambda button = addTeamsButton, n = i: self.selectTeams(button, n))
            addTeamsButton.place(x = 185, y = 280, anchor = "center")

            self.divFrames.append(frame)

        self.divFrames[0].pack(expand = True, fill = "both")
    
    def selectTeams(self, button, frameIndex):

        if self.addFrames[frameIndex] != 1: # the teams cannot be added (because the divison before it has not been completed)
            return
        
        button.place_forget()

        self.selectedVar = ctk.IntVar(value = 0)
        self.selectionFrame = ctk.CTkScrollableFrame(self.divFrames[frameIndex], fg_color = ORANGE_BG, width = 200, height = 400)
        self.selectionFrame.place(x = 185, y = 280, anchor = "center")

        self.createTableFrame = ctk.CTkFrame(self.divFrames[frameIndex], fg_color = ORANGE_BG, width = 223, height = 60)
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

        if (len(self.teams) < self.numTeams): # not enough teams have been created
            ctk.CTkLabel(self.selectionFrame, text = "Not enough teams\n have been created for\n a division of " + str(self.numTeams) + " teams", fg_color = ORANGE_BG, text_color = "white", font = (APP_FONT_BOLD, 15)).grid(row = 10, column = 0, columnspan = 3)
        else:
            for i in range(len(self.teams)):
                src = Image.open(self.teams[i]["logoPath"])
                logo = ctk.CTkImage(src, None, (20, 20))
                ctk.CTkLabel(self.selectionFrame, text = "", image = logo, fg_color = ORANGE_BG).grid(row = i + 3, column = 0)

                ctk.CTkLabel(self.selectionFrame, text = self.teams[i]["name"], fg_color = ORANGE_BG, text_color = "black", font = (APP_FONT_BOLD, self.getFont(self.teams[i]["name"]))).grid(row = i + 3, column = 1, padx = 10)
                checkBox = ctk.CTkCheckBox(self.selectionFrame, text = "", fg_color = ORANGE_BG, command = lambda n = i: self.checkboxClicked(self.teams[n]))
                checkBox.grid(row = i + 3, column = 2, padx = 10)
                self.checkBoxes.append(checkBox)

            self.selectButton = ctk.CTkButton(self.createTableFrame, text = "Create Table", fg_color = GRAY, state = "disabled", command = lambda: self.addTeams(self.selectedTeams, frameIndex))
            self.selectButton.place(x = 107, y = 40, anchor = "center")

            self.selectedLabel = ctk.CTkLabel(self.createTableFrame, text = "Selected: " + str(self.selectedVar.get()) + " teams", fg_color = ORANGE_BG, font = (APP_FONT_BOLD, 15))
            self.selectedLabel.place(x = 107, y = 10, anchor = "center")

    def checkboxClicked(self, team):
        if team in self.selectedTeams:
            self.selectedTeams.remove(team)
            self.selectedVar.set(self.selectedVar.get() - 1)
        else:
            self.selectedTeams.append(team)
            self.selectedVar.set(self.selectedVar.get() + 1)

        self.selectedLabel.configure(text = "Selected: " + str(self.selectedVar.get()) + " teams")

        if (self.selectedVar.get() == self.numTeams):
            self.selectButton.configure(state = "normal")
        else:
            self.selectButton.configure(state = "disabled")

    def addTeams(self, data, frameIndex, imported = False):
        self.data = data 

        if not imported:
            self.addFrames[frameIndex] = 0 # set to 0 as teams have been added to the div
            if frameIndex + 1 != self.divisions:
                self.addFrames[frameIndex + 1] = 1 # set to 1 as the next div can now have teams added

                self.selectedVar.set(0) # reset the selectedVar

                for team in self.selectedTeams: # remove any teams that have been selected
                    self.teams.remove(team)
                    
                self.selectedTeams = [] # reset the selectedTeams
            
            frame = self.divFrames[frameIndex] # delete every widget in the frame so the table can be added
            for widget in frame.winfo_children():
                widget.place_forget()

            tableFrame = self.createTableGrid(frame)
            self.data.sort(key = lambda x: x["name"])

            labels = []
            tableLogos2 = []
            for i in range(self.numTeams):
                teamLabels = []

                numLabel = ctk.CTkLabel(tableFrame, text = i + 1, fg_color = GRAY, text_color = "black")
                numLabel.grid(row = i + 1, column = 0)

                if i < self.numPromotions and frameIndex != 0:
                    src = Image.open("Images/promCircle.png")
                    img = ctk.CTkImage(src, None, (15, 15))
                    numLabel.configure(image = img)
                if i >= self.numTeams - self.numPromotions and frameIndex != self.divisions - 1:
                    src = Image.open("Images/relCircle.png")
                    img = ctk.CTkImage(src, None, (15, 15))
                    numLabel.configure(image = img)
                        
                src = Image.open(self.data[i]["logoPath"])
                logo = ctk.CTkImage(src, None, (20, 20))
                logoLabel = ctk.CTkLabel(tableFrame, text = "", image = logo, fg_color = GRAY)
                logoLabel.grid(row = i + 1, column = 1)
                tableLogos2.append(logoLabel)

                nameLabel = ctk.CTkLabel(tableFrame, text = self.data[i]["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 12))
                nameLabel.grid(row = i + 1, column = 2, sticky = "w")
                teamLabels.append(nameLabel)

                for j in range(8):
                    label = ctk.CTkLabel(tableFrame, text = "0", fg_color = GRAY, text_color = "black", font = (APP_FONT, 15))
                    label.grid(row = i + 1, column = j + 3)

                    teamLabels.append(label)

                labels.append(teamLabels)
                self.parent.matchesMenu.positions[str(frameIndex + 1)][self.data[i]["name"]] = []
                self.parent.matchesMenu.points[str(frameIndex + 1)][self.data[i]["name"]] = []
                
            self.tableLogos.append(tableLogos2)
            self.tableTeams.append(labels)
            self.records = [[0, 0, 0, 0, 0, 0] for i in range(self.numTeams)]

            self.finishedTables[frameIndex] = 1
            self.saveData(frameIndex)
            self.parent.matchesMenu.importBans()

        else:
            self.parent.matchesMenu.positions = {str(i + 1): {} for i in range(self.divisions)}
            self.parent.matchesMenu.points = {str(i + 1): {} for i in range(self.divisions)}

            i = 0
            while i != frameIndex + 1: # sets the addFrames list to 0 for all divisions that are being imported
                self.addFrames[i] = 0
                i += 1

            dictEntries = ["gp", "w", "d", "l", "gf", "ga", "gd", "p"]
            if frameIndex + 1 != self.divisions:
                self.addFrames[frameIndex + 1] = 1

                ## generated by co-pilot
                teamsRemove = [team2 for division in self.data["divisions"] for team2 in division["teams"]]
                self.teams = [team1 for team1 in self.teams if team1["name"] not in [team["name"] for team in teamsRemove]]
               
            for index, division in enumerate(self.data["divisions"]):
                frame = self.divFrames[index]
                tableFrame = self.createTableGrid(frame)
                
                tableLogos2 = []
                labels = []
                for i, team in enumerate(division["teams"]):
                    teamLabels = []

                    numLabel = ctk.CTkLabel(tableFrame, text = i + 1, fg_color = GRAY, text_color = "black")
                    numLabel.grid(row = i + 1, column = 0)

                    if i < self.numPromotions and index != 0:
                        src = Image.open("Images/promCircle.png")
                        img = ctk.CTkImage(src, None, (15, 15))
                        numLabel.configure(image = img)
                    if i >= self.numTeams - self.numPromotions and index != self.divisions - 1:
                        src = Image.open("Images/relCircle.png")
                        img = ctk.CTkImage(src, None, (15, 15))
                        numLabel.configure(image = img)

                    src = Image.open(team["logoPath"])
                    logo = ctk.CTkImage(src, None, (20, 20))
                    logoLabel = ctk.CTkLabel(tableFrame, text = "", image = logo, fg_color = GRAY)
                    logoLabel.grid(row = i + 1, column = 1)
                    tableLogos2.append(logoLabel)

                    nameLabel = ctk.CTkLabel(tableFrame, text = division["teams"][i]["name"], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 12))
                    nameLabel.grid(row = i + 1, column = 2, sticky = "w")
                    teamLabels.append(nameLabel)

                    self.parent.matchesMenu.positions[str(index + 1)][team["name"]] = division["teams"][i]["positions"]
                    self.parent.matchesMenu.points[str(index + 1)][team["name"]] = division["teams"][i]["points"]

                    for j in range(8):
                        label = ctk.CTkLabel(tableFrame, text = division["teams"][i][dictEntries[j]], fg_color = GRAY, text_color = "black", font = (APP_FONT, 15))
                        label.grid(row = i + 1, column = j + 3)

                        teamLabels.append(label)
                        
                    labels.append(teamLabels)
            
                self.tableLogos.append(tableLogos2)
                self.tableTeams.append(labels)

                if index == frameIndex:
                        break
            
            self.parent.matchesMenu.sortTable()
            self.finishedTables[frameIndex] = 1

    def createTableGrid(self, frame):
        tableFrame = ctk.CTkFrame(frame, fg_color = GRAY)
        tableFrame.pack(expand = True, fill = "both")
        tableFrame.grid_propagate(False)

        tableFrame.grid_columnconfigure(0, weight = 3)
        tableFrame.grid_columnconfigure(1, weight = 6)
        tableFrame.grid_columnconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight = 1)
        tableFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)

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

        return tableFrame

    def saveData(self, frameIndex):
        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)

            with open("teams.json", "r") as file:
                teamsBasic = json.load(file)
            
            with open("players.json", "r") as file:
                teamsData = json.load(file)
        except:
            data = []
            teamsBasic = []
            teamsData = []

        for league in data:
            if league['name'] == self.name:
                teams = league["divisions"][frameIndex]["teams"]

        for team in self.tableTeams[frameIndex]:
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

        for team in teamsBasic:
            if(team["name"] in [team[0].cget("text") for team in self.tableTeams[frameIndex]]):
                if self.name not in team["competitions"]:
                    team["competitions"].append(self.name)

        for team in teamsData:
            if(team["name"] in [team[0].cget("text") for team in self.tableTeams[frameIndex]]):
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

    def getFont(self, string):
        if (len(string) <= 10):
            return 15
        if (len(string) < 15):
            return 12
        if (len(string) >= 15):
            return 8

    def checkAllBoxes(self, check):
        for i in range(len(self.teams)):
            if check and self.checkBoxes[i].get() == 0:
                self.checkBoxes[i].select()
                self.checkboxClicked(self.teams[i])
            elif not check and self.checkBoxes[i].get() == 1:
                self.checkBoxes[i].deselect()
                self.checkboxClicked(self.teams[i])

class MatchesMenu(ctk.CTkFrame):
    def __init__(self, parent, divisionsMenu, numTeams, divisions):
        super().__init__(parent)
        self.pack(expand = True, fill = "both")

        self.parent = divisionsMenu
        self.numTeams = numTeams
        self.divisions = divisions

        self.schedule = []
        self.scores = []
        self.activeFrame = 0
        self.activeSim = [0] * ((numTeams * 2) - 2) 
        self.scoreLabels = []
        self.matchesFrames = []
        self.line = "--------------------------------------------------------------------------------------------------------------------------------"
        self.matchesInfo = [] 
        self.lineups = [] 
        self.referees = [] 
        self.injuries = [] 
        self.positions = {str(i + 1): {} for i in range(self.divisions)}
        self.points = {str(i + 1): {} for i in range(self.divisions)}
        self.banned = []
        self.ratings = []
        self.playersData = []
        self.playersOTM = []

        self.topScorer = []
        self.topAssister = []
        self.topAverageRating = []
        self.topCleanSheet = []
        self.topPen = []
        self.topPOTM = []

        self.rowStart = [1]
        rowStep = int((self.numTeams / 2) + 1)
        for i in range(1, self.divisions):
            self.rowStart.append(self.rowStart[i - 1] + rowStep)
        
        self.createMatchesButton = ctk.CTkButton(self, text = "Create Matches", fg_color = ORANGE_BG, command = lambda: self.createMatches())
        self.createMatchesButton.place(x = 185, y = 280, anchor = "center")

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
            if league["name"] == self.parent.tableMenu.name:
                I = index
                if league["divisions"][0]["matchDays"] != []:
                    foundMatches = True
                else:
                    foundMatches = False
                
                break
        
        for div in leaguesData[I]["divisions"]:
            data = []
            for team in div["teams"]:
                entry = {
                        "name": team["name"],
                        "players": []
                    }
            
                for teamPlayers in playersData:
                    if teamPlayers["name"] == team["name"]:
                        for player in teamPlayers["players"]:
                            entry["players"].append(player)
                
                data.append(entry)
        
            self.playersData.append(data)
        
        # print(self.playersData)
        
        if not foundMatches:
            self.activeSim[0] = 1
            return
        else:
            self.createMatchesButton.place_forget()
            self.createFrames()

            breakLoop = False
            for index, matchDay in enumerate(leaguesData[I]["divisions"][0]["matchDays"]):
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

            # for frame, matchDay in zip(self.matchesFrames, div["matchDays"]):
            for matchDayIndex in range((self.numTeams * 2) - 2):
                matches = []
                labels1 = []
                matchDayInfo = []
                matchDayLineups = []
                matchDayReferees = []
                matchDayInjuries = []
                matchDayRatings = []
                matchDayPlayersOTM = []
                matchDayScores = []
                # yPlaceIndex = 0
                
                # yPlaces = [60 + 50 * i for i in range(51)] # 48 possible matchdays + 3 divider lines
                # xPlaces = [105, 145, 180, 215, 255]
                frame = self.matchesFrames[matchDayIndex]
                for j, div in enumerate(leaguesData[I]["divisions"]):
                    matchDay = div["matchDays"][matchDayIndex]

                    games = []
                    labels2 = []
                    matchDayInfo2 = []
                    matchDayLineups2 = []
                    matchDayReferees2 = []
                    matchDayInjuries2 = []
                    matchDayRatings2 = []
                    matchDayPlayersOTM2 = []
                    matchDayScores2 = []

                    for index, match in enumerate(matchDay["matches"]):
                        match_ = [0, 0]

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
                            matchDayInfo2.append(matchInfo)
                            matchDayLineups2.append(matchLineups)
                            matchDayReferees2.append(referee)
                            matchDayInjuries2.append(injury)
                            matchDayRatings2.append(matchRatings)
                            matchDayPlayersOTM2.append(playerOTM)
                            matchDayScores2.append([homeTeam, awayTeam, score])
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

                        packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 60, width = 200)
                        packFrame.pack(expand = True, fill = "both")
                        ctk.CTkLabel(packFrame, text = homeTeam, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(homeTeam) > 15 else 12)).place(relx = 0.3, rely = 0.5, anchor = "ne")
                        ctk.CTkLabel(packFrame, text = "", image = logoHome, fg_color = GRAY).place(relx = 0.4, rely = 0.5, anchor = "ne")

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
                            scoreLabel = ctk.CTkLabel(packFrame, text = "[ " + score + " ]", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))

                            scoreLabel.bind("<Enter> <Button-1>", lambda event, scoreLabel = scoreLabel, time = time, home = home, away = away, matchInfo = matchInfo, matchLineups = matchLineups, matchRatings = matchRatings, referee = referee, injury = injury, playerOTM = playerOTM: self.openMatch(scoreLabel, time, home, away, matchInfo, matchLineups, matchRatings, referee, injury, playerOTM, True))
                        else:
                            scoreLabel = ctk.CTkLabel(packFrame, text = score, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))
                        scoreLabel.place(relx = 0.5, rely = 0.7, anchor = "center")

                        # yPlaces = [60 + 50 * i for i in range(51)] # 48 possible matchdays + 3 divider lines
                        redSrc = Image.open("Images/redCard.png")
                        redCard = ctk.CTkImage(redSrc, None, (10, 10))
                        injSrc = Image.open("Images/injury.png")
                        inj = ctk.CTkImage(injSrc, None, (10, 10))

                        if homeLabels != "none":
                            if homeLabels == "red":
                                ctk.CTkLabel(packFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                            elif homeLabels == "inj":
                                ctk.CTkLabel(packFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                            else:
                                ctk.CTkLabel(packFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                                ctk.CTkLabel(packFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 160, y = 20, anchor = "nw")

                        if awayLabels != "none":
                            if awayLabels == "red":
                                ctk.CTkLabel(packFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                            elif awayLabels == "inj":
                                ctk.CTkLabel(packFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                            else:
                                ctk.CTkLabel(packFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                                ctk.CTkLabel(packFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 177, y = 20, anchor = "nw")

                        # yPlaces[yIndex] - 5 for all red cards, injuries
                        ctk.CTkLabel(packFrame, text = "", image = logoAway, fg_color = GRAY).place(relx = 0.6, rely = 0.5, anchor = "nw")
                        ctk.CTkLabel(packFrame, text = awayTeam, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(awayTeam) > 15 else 12)).place(relx = 0.7, rely = 0.5, anchor = "nw")
                        labels2.append(scoreLabel) 

                        match_[0] = homeTeam
                        match_[1] = awayTeam
                        games.append(match_)

                        # yPlaceIndex += 1
                    
                    if j < self.divisions - 1:
                        packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 20, width = 200)
                        packFrame.pack(expand = True, fill = "both", pady = (15, 0))
                        ctk.CTkLabel(packFrame, text = self.line, text_color = "black", fg_color = GRAY).place(relx = 0.5, rely = 0.5, anchor = "center")
                        # yPlaceIndex += 1

                    labels1.append(labels2)
                    matches.append(games)

                    matchDayInfo.append(matchDayInfo2)
                    matchDayLineups.append(matchDayLineups2)
                    matchDayReferees.append(matchDayReferees2)
                    matchDayInjuries.append(matchDayInjuries2)
                    matchDayRatings.append(matchDayRatings2)
                    matchDayPlayersOTM.append(matchDayPlayersOTM2)
                    matchDayScores.append(matchDayScores2)

                if add:
                    self.matchesInfo.append(matchDayInfo)
                    self.lineups.append(matchDayLineups)
                    self.referees.append(matchDayReferees)
                    self.injuries.append(matchDayInjuries)
                    self.ratings.append(matchDayRatings)
                    self.playersOTM.append(matchDayPlayersOTM)
                    self.scores.append(matchDayScores)

                self.scoreLabels.append(labels1)
                self.schedule.append(matches) 
                self.matchesFrames[0].place(x = 0, y = 0, anchor = "nw")
                self.actionButtonsFrame.place(x = 0, y = 587, anchor = "nw")

    def importBans(self):
        self.banned = []

        try:
            with open("players.json", "r") as file:
                players = json.load(file)
        except:
            players = []

        if self.parent.tableMenu.finishedTables[self.divisions - 1] == 0:
            return
        
        for team in players:
            if team["name"] in [team[0].cget("text") for i in range(self.divisions) for team in self.parent.tableMenu.tableTeams[i]]:
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
        self.createMatchesButton.place_forget()

        for i in range((self.numTeams * 2) - 2):
            frame = ctk.CTkScrollableFrame(self, fg_color = GRAY, height = 572, width = 345)

            packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 25, width = 200)
            frame.matchDayLabel = ctk.CTkLabel(packFrame, text = "Matchday " + str(i + 1), fg_color = GRAY, font = (APP_FONT_BOLD, 15))
            frame.matchDayLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
            packFrame.pack(expand = True, fill = "both")

            frame.currentMatchDayButton = ctk.CTkButton(packFrame, text = "Current Matchday", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = self.currentMatchDay) # button to go back to the current matchday
            
            self.matchesFrames.append(frame)

        self.actionButtonsFrame = ctk.CTkFrame(self, fg_color = GRAY, height = 40, width = 367)

        self.leftArrow = ctk.CTkButton(self.actionButtonsFrame, text = "<", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.changeFrame(-1))
        self.leftArrow.place(x = 60, rely = 0.5, anchor = "center")

        self.rightArrow = ctk.CTkButton(self.actionButtonsFrame, text = ">", fg_color = ORANGE_BG, width = 50, bg_color = GRAY, height = 15, command = lambda: self.changeFrame(1))
        self.rightArrow.place(x = 310, rely = 0.5, anchor = "center")

        self.simulateButton = ctk.CTkButton(self.actionButtonsFrame, text = "Simulate", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.simMatchDay())
        self.simulateButton.place(x = 230, rely = 0.5, anchor = "center")

        self.autoButton = ctk.CTkButton(self.actionButtonsFrame, text = "Auto", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.automateMatches())
        self.autoButton.place(x = 140, rely = 0.5, anchor = "center")

        self.pauseButton = ctk.CTkButton(self.actionButtonsFrame, text = "Pause", fg_color = ORANGE_BG, bg_color = GRAY, width = 50, height = 15, command = lambda: self.pauseSim())

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

    def createMatches(self):
        if self.parent.tableMenu.finishedTables[self.divisions - 1] == 1:
            numTeams = str((self.numTeams * 2) - 2)
            progressLabel = ctk.CTkLabel(self, text = "Matchdays created: 0 / " + numTeams, font = (APP_FONT, 20), text_color  = "white")
            progressLabel.place(x = 185, y = 350, anchor = "center")
            progressLabel.update_idletasks()
            self.createFrames()
        else:
            return

        times = ["12:30", "13:00", "14:00", "15:00", "17:00", "19:00", "20:00"]
        teamNames = []

        try:
            with open("players.json", "r") as file:
                players = json.load(file)
        except:
            players = []

        for division in self.parent.tableMenu.tableTeams:
            names = []
            entries = []
            for team in division:
                names.append(team[0].cget("text"))

                entry = {
                    "name": team[0].cget("text"),
                    "players": []
                }

                for teamPlayers in players:
                    if teamPlayers["name"] == team[0].cget("text"):
                        for player in teamPlayers["players"]:
                            entry["players"].append(player)

                entries.append(entry)

            teamNames.append(names)
            self.playersData.append(entries)

        for div in teamNames:
            random.shuffle(div)

        ## algorithm to create the schedule
        self.schedule = []

        for i in range(len(teamNames[0]) - 1):
            matchDay = []
            for division in teamNames:
                pairs = []
                for j in range(len(division) // 2):
                    if i % 2 == 0:
                        pairs.append((division[j], division[-j - 1], random.choice(times)))
                    else:
                        pairs.append((division[-j - 1], division[j], random.choice(times)))
                division.insert(1, division.pop())
                matchDay.append(pairs)
            self.schedule.append(matchDay)

            for division in teamNames:
                division.insert(1, division.pop())

        # Second round (home and away)
        second_round = []
        for matchDay in self.schedule:
            second_round_day = []
            for division_matches in matchDay:
                second_round_day.append([(away, home, time) for home, away, time in division_matches])
            second_round.append(second_round_day)

        self.schedule += second_round
        ## end of algorithm

        # Sort matches by time within each division
        for matchDay in self.schedule:
            for division in matchDay:
                division.sort(key = lambda match: match[2])
                
        # yPlaceIndex = 0 
        # yPlaces = [60 + 50 * i for i in range(51)]
        # xPlaces = [105, 145, 180, 215, 255]

        for matchDayIndex, matchDay in enumerate(self.schedule):
        # for j, division in enumerate(self.schedule):
            labels1 = []
            # for i, day in enumerate(division):
            for i, div in enumerate(matchDay):
                frame = self.matchesFrames[matchDayIndex]

                labels2 = []
                for match in div:
                    teamHome = match[0]
                    teamAway = match[1]
                    time = match[2]

                    srcHome = Image.open("SavedImages/Teams/" + teamHome + ".png")
                    logoHome = ctk.CTkImage(srcHome, None, (30, 30))

                    srcAway = Image.open("SavedImages/Teams/" + teamAway + ".png")
                    logoAway = ctk.CTkImage(srcAway, None, (30, 30))

                    packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 60, width = 200)
                    packFrame.pack(expand = True, fill = "both")
                    ctk.CTkLabel(packFrame, text = match[0], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(teamHome) > 15 else 12)).place(relx = 0.3, rely = 0.5, anchor = "ne")
                    ctk.CTkLabel(packFrame, text = "", image = logoHome, fg_color = GRAY).place(relx = 0.4, rely = 0.5, anchor = "ne")
                    scoreLabel = ctk.CTkLabel(packFrame, text = time, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15))
                    scoreLabel.place(relx = 0.5, rely = 0.7, anchor = "center")
                    ctk.CTkLabel(packFrame, text = "", image = logoAway, fg_color = GRAY).place(relx = 0.6, rely = 0.5, anchor = "nw")
                    ctk.CTkLabel(packFrame, text = match[1], fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 10 if len(teamAway) > 15 else 12)).place(relx = 0.7, rely = 0.5, anchor = "nw")

                    labels2.append(scoreLabel)
                    # yPlaceIndex += 1
                
                labels1.append(labels2)
                if i < self.divisions - 1:
                    packFrame = ctk.CTkFrame(frame, fg_color = GRAY, height = 20, width = 200)
                    packFrame.pack(expand = True, fill = "both", pady = (15, 0))
                    ctk.CTkLabel(packFrame, text = self.line, text_color = "black", fg_color = GRAY).place(relx = 0.5, rely = 0.5, anchor = "center")
                    # yPlaceIndex += 1
            
            progressLabel.configure(text = "Matchdays created: " + str(matchDayIndex + 1) + " / " + numTeams)
            progressLabel.update_idletasks()

            self.scoreLabels.append(labels1)
        
        progressLabel.destroy()
        self.matchesFrames[0].place(x = 0, y = 0, anchor = "nw")
        self.actionButtonsFrame.place(x = 0, y = 587, anchor = "nw")
        self.activeSim[0] = 1
        self.saveMatches()

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

        for matchDayIndex, matchDay in enumerate(self.schedule, 1):
            for i, div in enumerate(matchDay):
                matches = []
                for match in div:
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
            
                leaguesData[I]["divisions"][i]["matchDays"].append({
                    "matchDay": matchDayIndex,
                    "matches": matches
                })

        with open("leaguesData.json", "w") as file:
            json.dump(leaguesData, file, indent = 4)

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
            teamsData = []
            teams = []
            leagues = []

        for league in leagues:
            if league["name"] == self.parent.name:
                matchReferees = league["referees"]

        matches = self.schedule[self.activeFrame] # in the form [[], [], []] where each list contais the matches for each division for that matchday
        matchDayScores = []
        matchDayInfo = []
        matchDayLineups = []
        matchDayReferees = []
        matchDayInjuries = []
        matchDayRatings = []
        matchDayPlayersOTM = []

        for i, matchesDiv in enumerate(matches):
            matchDayScores2 = []
            matchDayInfo2 = []
            matchDayLineups2 = []
            matchDayReferees2 = []
            matchDayInjuries2 = []
            matchDayRatings2 = []
            matchDayPlayersOTM2 = []

            for index, match in enumerate(matchesDiv):
                homeTeam = match[0]
                awayTeam = match[1]
                referee = random.choice(matchReferees)
                matchDayReferees2.append(referee)
                matchReferees.remove(referee)

                for teamIndex, team in enumerate(teams):
                    if team["name"] == homeTeam:
                        homeTeam = team
                        homeBasic = teamsData[teamIndex]
                    if team["name"] == awayTeam:
                        awayTeam = team
                        awayBasic = teamsData[teamIndex]

                homeTeamLineup = self.getLineup(homeTeam)
                awayTeamLineup = self.getLineup(awayTeam)
                lineups = [homeTeamLineup, awayTeamLineup]

                winner = self.decideWinner(homeBasic, awayBasic) 
                levelDiff = abs(homeBasic["level"] - awayBasic["level"]) 
                score = self.generateScore(winner, homeBasic, awayBasic, levelDiff) 

                redCard, redTeam = self.getReds(homeTeamLineup, awayTeamLineup, homeTeam, awayTeam, winner)
                injury, injTeam = self.getInjury(homeTeamLineup, awayTeamLineup)
                homeMissedPens = self.getMissedPens(homeTeamLineup)
                awayMissedPens = self.getMissedPens(awayTeamLineup)
                homeScorers = self.getScorers(homeTeamLineup, awayTeamLineup, score[homeTeam["name"]], redCard, homeMissedPens)
                awayScorers = self.getScorers(awayTeamLineup, homeTeamLineup, score[awayTeam["name"]], redCard, awayMissedPens)
                homeRatings = self.getRatings(homeTeam["name"], homeScorers, awayScorers, homeTeamLineup, winner, score[awayTeam["name"]])
                awayRatings = self.getRatings(awayTeam["name"], awayScorers, homeScorers, awayTeamLineup, winner, score[homeTeam["name"]])
                matchRatings = [homeRatings, awayRatings]

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

                matchDayPlayersOTM2.append(playerOTM)
                    
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
                label = self.scoreLabels[self.activeFrame][i][index]
                time = label.cget("text")

                label.configure(text = "[ " + str(score[homeTeam["name"]]) + " : " + str(score[awayTeam["name"]]) + " ]")
                label.bind("<Enter> <Button-1>", lambda event, label = label, time = time, homeTeam = homeBasic, awayTeam = awayBasic, matchInfo = matchInfo, lineups = lineups, matchRatings = matchRatings, referee = referee, injury = injury, playerOTM = playerOTM: self.openMatch(label, time, homeTeam, awayTeam, matchInfo, lineups, matchRatings, referee, injury, playerOTM))

                redSrc = Image.open("Images/redCard.png")
                redCard = ctk.CTkImage(redSrc, None, (10, 10))
                injSrc = Image.open("Images/injury.png")
                inj = ctk.CTkImage(injSrc, None, (10, 10))
                matchFrame = label._root().nametowidget(label.winfo_parent())

                if homeLabels != "none":
                    if homeLabels == "red":
                        ctk.CTkLabel(matchFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                    elif homeLabels == "inj":
                        ctk.CTkLabel(matchFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                    else:
                        ctk.CTkLabel(matchFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 150, y = 20, anchor = "nw")
                        ctk.CTkLabel(matchFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 160, y = 20, anchor = "nw")

                if awayLabels != "none":
                    if awayLabels == "red":
                        ctk.CTkLabel(matchFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                    elif awayLabels == "inj":
                        ctk.CTkLabel(matchFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                    else:
                        ctk.CTkLabel(matchFrame, text = "", image = redCard, fg_color = GRAY, height = 10, width = 10).place(x = 187, y = 20, anchor = "nw")
                        ctk.CTkLabel(matchFrame, text = "", image = inj, fg_color = GRAY, height = 10, width = 10).place(x = 177, y = 20, anchor = "nw")

                team1Data = [homeTeam["name"], 1 if winner == homeTeam["name"] else 0, 1 if winner == "Draw" else 0, 1 if winner == awayTeam["name"] else 0, score[homeTeam["name"]], score[awayTeam["name"]], score[homeTeam["name"]] - score[awayTeam["name"]], 0]
                team2Data = [awayTeam["name"], 1 if winner == awayTeam["name"] else 0, 1 if winner == "Draw" else 0, 1 if winner == homeTeam["name"] else 0, score[awayTeam["name"]], score[homeTeam["name"]], score[awayTeam["name"]] - score[homeTeam["name"]], 0]

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

                matchDayInfo2.append(matchInfo)
                matchDayLineups2.append(lineups)
                matchDayInjuries2.append(injury)
                matchDayRatings2.append(matchRatings)   
                matchDayScores2.append([homeTeam["name"], awayTeam["name"], str(score[homeTeam["name"]]) + " : " + str(score[awayTeam["name"]])])

                self.activeSim[self.activeFrame] = 0 
                if (self.activeFrame != (self.numTeams * 2) - 3): 
                    self.activeSim[self.activeFrame + 1] = 1 

            matchDayReferees.append(matchDayReferees2)
            matchDayInfo.append(matchDayInfo2)
            matchDayLineups.append(matchDayLineups2)
            matchDayInjuries.append(matchDayInjuries2)
            matchDayRatings.append(matchDayRatings2)
            matchDayPlayersOTM.append(matchDayPlayersOTM2)
            matchDayScores.append(matchDayScores2)
            # self.scores[i][self.activeFrame] = scores2
        
        self.referees.append(matchDayReferees)
        self.injuries.append(matchDayInjuries)
        self.matchesInfo.append(matchDayInfo)
        self.lineups.append(matchDayLineups)
        self.ratings.append(matchDayRatings)
        self.playersOTM.append(matchDayPlayersOTM)
        self.scores.append(matchDayScores)
        
        self.updateStats()
        self.sortTable() 
        self.updatePositions(self.activeFrame + 1)
        self.reduceMatchBans() 
        self.matchesFrames[self.activeFrame].matchDayLabel.place_forget()
        self.matchesFrames[self.activeFrame].matchDayLabel.place(relx = 0.69, rely = 0.5, anchor = "center")
        self.matchesFrames[self.activeFrame].currentMatchDayButton.place(relx = 0.3, rely = 0.5, anchor = "center")

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
        
    def generateScore(self, winner, team1, team2, level_diff):
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
            if level_diff < 10:
                winningGoalsChoices = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3]
                losingGoalsChoices = [0, 1, 1, 2]
            elif level_diff <= 20:
                winningGoalsChoices = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]
                losingGoalsChoices = [0, 1, 1, 2, 2, 3]
            elif level_diff < 30:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2, 2]
            else:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 7, 8]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2]

        # get the score
        winningGoals = random.choice(winningGoalsChoices)
        losingGoals = random.choice(losingGoalsChoices)

        # if the goals scored by the losing team is more than the winning team, get a score until it isn't
        while losingGoals >= winningGoals:
            losingGoals = random.choice(losingGoalsChoices)

        return {winningTeam["name"]: winningGoals, losingTeam["name"]: losingGoals}

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
            
            for div in self.playersData:
                for team in div:
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

                if not playerFound:
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

                            break

                playerMatches.append(matchEntry)

    def updateStats(self):
        # find the top scorer and top assister
        topScorers = [{"name": "", "goals": 0, "team": ""} for _ in range (10)]
        topAssisters = [{"name": "", "assists": 0, "team": ""} for _ in range(10)]
        topAverageRatings = [{"name": "", "rating": 0.00, "team": ""} for _ in range(10)]
        topCleanSheets = [{"name": "", "cleanSheets": 0, "team": ""} for _ in range(10)]
        topPens = [{"name": "", "pens": 0, "team": ""} for _ in range(10)]
        topPOTM = [{"name": "", "playerOTM": 0, "team": ""} for _ in range(10)]

        allScorers = []
        allAssisters = []
        allRatings = []
        allCleanSheets = []
        allPens = []
        allPOTM = []

        numMatchdays = (self.numTeams * 2) - 2
        averageRatingBaseline = numMatchdays / 8 # players need to have played at least 1/8 of the games to be considered for the top average rating

        compIndex = None
        for team in self.playersData[0]: # only look at first division
            for player in team["players"]:
                if player["seasonStats"] != []:
                    
                    if compIndex is None:
                        for comp in player["seasonStats"]:
                            if comp["compName"] == self.parent.name:
                                compIndex = player["seasonStats"].index(comp)

                    seasonStats = player["seasonStats"][compIndex]

                    allScorers.append({
                        "name": player["name"],
                        "stat": seasonStats["goals"],
                        "team": team["name"]
                    })

                    allAssisters.append({
                        "name": player["name"],
                        "stat": seasonStats["assists"],
                        "team": team["name"]
                    })

                    if seasonStats["played"] > averageRatingBaseline:
                        allRatings.append({
                            "name": player["name"],
                            "stat": seasonStats["averageRating"],
                            "team": team["name"]
                        })

                    allPOTM.append({
                        "name": player["name"],
                        "stat": seasonStats["MOTM"],
                        "team": team["name"]
                    })
                
                    if player["position"] == "goalkeeper":
                        allCleanSheets.append({
                            "name": player["name"],
                            "stat": seasonStats["clean sheets"],
                            "team": team["name"]
                        })
                
                    if player["position"] == "forward":
                        allPens.append({
                            "name": player["name"],
                            "stat": seasonStats["pens"],
                            "team": team["name"]
                        })

        # Sort players by goals and assists in descending order
        topScorers = heapq.nlargest(7, allScorers, key=lambda x: x["stat"])
        topAssisters = heapq.nlargest(7, allAssisters, key=lambda x: x["stat"])
        topAverageRatings = heapq.nlargest(7, allRatings, key=lambda x: x["stat"])
        topCleanSheets = heapq.nlargest(7, allCleanSheets, key=lambda x: x["stat"])
        topPens = heapq.nlargest(7, allPens, key=lambda x: x["stat"])
        topPOTM = heapq.nlargest(7, allPOTM, key=lambda x: x["stat"])

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
        self.matchesFrames[self.activeFrame].place_forget()
    
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
                elif re.search(r'\b(?:I{1,3})\b', scorerName[-1], re.IGNORECASE):
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

    def updateTable(self, teamData):
        for index, div in enumerate(self.parent.tableMenu.tableTeams):
            for team in div:
                if team[0].cget("text") == teamData[0]:
                    team[1].configure(text = str(int(team[1].cget("text")) + 1))

                    for i in range(1, 8):
                        team[i + 1].configure(text = str(int(team[i + 1].cget("text")) + teamData[i]))

                    for teamEntry in self.points[str(index + 1)]:
                        if teamEntry == team[0].cget("text"):
                            self.points[str(index + 1)][teamEntry].append(int(team[8].cget("text")))

    def sortTable(self, points = True):
        tableTeams = self.parent.tableMenu.tableTeams
        tableLogos = self.parent.tableMenu.tableLogos

        sortedTeams = []
        if points == True:
            for div in tableTeams:
                sort = sorted(div, key = lambda x: (int(x[8].cget("text")), int(x[7].cget("text")), int(x[5].cget("text"))), reverse = True)
                sortedTeams.append(sort)
        else:
            for div in tableTeams:
                sort = sorted(div, key = lambda x: x[0].cget("text"))
                sortedTeams.append(sort)

        sortedTexts = []
        for div in sortedTeams:
            texts = [[label.cget("text") for label in team] for team in div]
            sortedTexts.append(texts)

        try:
            with open("teams.json", "r") as file:
                teams = json.load(file)
        except:
            teams = []

        for i, div in enumerate(sortedTeams):
            for j, sortedTeam in enumerate(div):
                for k in range(len(sortedTeam)):
                    tableTeams[i][j][k].configure(text = sortedTexts[i][j][k])

                    for team in teams:
                        if team["name"] == sortedTexts[i][j][k]:
                            src = Image.open(team["logoPath"])
                            logo = ctk.CTkImage(src, None, (20, 20))
                            tableLogos[i][j].configure(image = logo)

    def saveTable(self):
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
            
            with open("players.json", "r") as file:
                teamsData = json.load(file)
        except:
            leaguesData = []
            teamsData = []

        for league in leaguesData:
            if league["name"] == self.parent.name:
                league["divisions"][0]["topScorer"] = self.topScorer
                league["divisions"][0]["topAssister"] = self.topAssister
                league["divisions"][0]["topAverageRating"] = self.topAverageRating
                league["divisions"][0]["topCleanSheet"] = self.topCleanSheet
                league["divisions"][0]["topPen"] = self.topPen
                league["divisions"][0]["topPOTM"] = self.topPOTM
                currLeague = league
                break
        
        for i, matchDayScores in enumerate(self.scores):
            for j, div in enumerate(matchDayScores):
                teams = currLeague["divisions"][j]["teams"]

                matchDayMatches = currLeague["divisions"][j]["matchDays"][i]["matches"]

                if self.parent.tableMenu.finishedTables[self.divisions - 1] == 1: # only save if teams have been added
                    for teamData in self.parent.tableMenu.tableTeams[j]:
                        for team in teams:
                            if team["name"] == teamData[0].cget("text"):
                                team["gp"] = teamData[1].cget("text")
                                team["w"] = teamData[2].cget("text")
                                team["d"] = teamData[3].cget("text")
                                team["l"] = teamData[4].cget("text")
                                team["gf"] = teamData[5].cget("text")
                                team["ga"] = teamData[6].cget("text")
                                team["gd"] = teamData[7].cget("text")
                                team["p"] = teamData[8].cget("text")

                                team["positions"] = self.positions[str(j+1)][team["name"]]
                                team["points"] = self.points[str(j+1)][team["name"]]

                for k, match_ in enumerate(div):
                    matchData = matchDayMatches[k]
                    if match_[0] == matchData["home"] and match_[1] == matchData["away"] and matchData["played"] == 0:
                        matchData["score"] = div[k][2]
                        matchData["played"] = 1

                        for (player, rating) in zip(self.lineups[i][j][k][0], self.ratings[i][j][k][0]):
                            entry = {
                                "name": player["name"],
                                "rating": rating
                            }
                            matchData["homeLineup"].append(entry)

                        for (player, rating) in zip(self.lineups[i][j][k][1], self.ratings[i][j][k][1]):
                            entry = {
                                "name": player["name"],
                                "rating": rating
                            }
                            matchData["awayLineup"].append(entry)
                        
                        scorers = sorted(self.matchesInfo[i][j][k][0], key = lambda x: int(str(x[3]).split("+")[0]) + int(str(x[3]).split("+")[1]) if "+" in str(x[3]) else int(x[3]))
                        for scorer in scorers:
                            entry = {
                                "name": scorer[0],
                                "assister": scorer[1],
                                "type": scorer[2],
                                "time": scorer[3]
                            }
                            matchData["homeScorers"].append(entry)

                        scorers = sorted(self.matchesInfo[i][j][k][1], key = lambda x: int(str(x[3]).split("+")[0]) + int(str(x[3]).split("+")[1]) if "+" in str(x[3]) else int(x[3]))
                        for scorer in scorers:
                            entry = {
                                "name": scorer[0],
                                "assister": scorer[1],
                                "type": scorer[2],
                                "time": scorer[3]
                            }
                            matchData["awayScorers"].append(entry)

                        matchData["referee"] = self.referees[i][j][k]
                        matchData["injured"] = self.injuries[i][j][k]
                        matchData["playerOTM"] = self.playersOTM[i][j][k]

                for team in teamsData:
                    if hasattr(self.parent.tableMenu, "tableTeams"):
                        for teamName in self.parent.tableMenu.tableTeams[j]:
                            if team["name"] == teamName[0].cget("text"):
                                teamList = None
                                for data in self.playersData[j]:
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

                                                # for match in playerData["matches"]:
                                                #     played += 1
                                                #     goals += match["goals"]
                                                #     assists += match["assists"]
                                                #     reds += match["red"]
                                                #     cleanSheets += match["clean sheet"]
                                                #     rating += match["rating"]

                                                # averageRating = rating / played

                                                for comp in player["seasonStats"]:
                                                    compIndex = player["seasonStats"].index(comp)
                                                    if comp["compName"] == self.parent.name:
                                                        comp["played"] = playerData["seasonStats"][compIndex]["played"]
                                                        comp["goals"] = playerData["seasonStats"][compIndex]["goals"]
                                                        comp["assists"] = playerData["seasonStats"][compIndex]["assists"]
                                                        comp["reds"] = playerData["seasonStats"][compIndex]["reds"]
                                                        comp["clean sheets"] = playerData["seasonStats"][compIndex]["clean sheets"]
                                                        comp["averageRating"] = playerData["seasonStats"][compIndex]["averageRating"]
                                                        # comp["averageRating"] = round((averageRating + comp["averageRating"]) / 2, 2) if comp["averageRating"] != 0 else round(averageRating, 2)
                                                        comp["pens"] = playerData["seasonStats"][compIndex]["pens"]
                                                        comp["MOTM"] = playerData["seasonStats"][compIndex]["MOTM"]
                                
                                # if teamList is not None:
                                #     teamList["players"] = [] # reset

        with open("players.json", "w") as file:
            json.dump(teamsData, file)

        with open("leaguesData.json", "w") as file:
            json.dump(leaguesData, file)

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

        for i, matchDay in enumerate(self.schedule, 1):
            for j, div in enumerate(matchDay): # loop through the schedule
                matches = [] # new entry for the matchDays part of the league data
                for match in div: # loop through the matches in a matchDay
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
                leaguesData[I]["divisions"][j]['matchDays'].append({
                    "matchday": i,
                    "matches": matches
                })

        with open('leaguesData.json', 'w') as file:
            json.dump(leaguesData, file)

    def updatePositions(self, matchDay):
        for i, div in enumerate(self.parent.tableMenu.tableTeams):
            for index, team in enumerate(div):
                for teamName in self.positions[str(i+1)].keys():
                    if team[0].cget("text") == teamName:
                        self.positions[str(i+1)][teamName].append(index + 1)
                                       
        if matchDay >= 2:
            graphsMenu = self.parent.graphsMenu
            graphsMenu.canvas.delete()
            graphsMenu.canvas = ctk.CTkCanvas(graphsMenu.canvasFrame, bg = GRAY, width = graphsMenu.canvasWidth, height = graphsMenu.canvasHeight, highlightthickness = 0)
            graphsMenu.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

            if graphsMenu.graph == "positions":
                graphsMenu.drawGrid(matchDay - 1)

                for i, team in enumerate(self.positions["1"]):
                    src = "SavedImages/Teams/" + team + ".png"
                    graphsMenu.addPoints(self.positions["1"][team], src, matchDay - 1, i)
            else:
                mostPoints = max(x[-1] for x in self.points["1"].values())
                graphsMenu.rows = int(mostPoints)
                graphsMenu.drawGrid(matchDay - 1)

                for i, team in enumerate(self.points["1"]):
                    src = "SavedImages/Teams/" + team + ".png"
                    graphsMenu.addPoints(self.points["1"][team], src, matchDay - 1, i)

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

        self.simulateAllMatchDays(startDay) # simulate the matchDays

    def simulateAllMatchDays(self, day):
        if not self.paused: # if not paused, simulation is ongoing so update the buttons
            self.autoButton.place_forget()
            self.pauseButton.place(x = 140, rely = 0.5, anchor = "center")
            self.simulateButton.configure(state = "disabled")

        if not self.paused and day < len(self.matchesFrames): # if not paused and the day is less than the total number of days, simulate the matchDay
            self.after(500, self.simMatchDay)

            self.after(2000, self.changeFrame, 1) # change the frame
            self.after(3000, self.simulateAllMatchDays, day + 1) # call the function again
        else: # once over, reset the arrow
            self.rightArrow.configure(state = "normal")
            self.leftArrow.configure(state = "normal")

            self.pauseButton.place_forget() # update the buttons
            self.autoButton.place(x = 140, rely = 0.5, anchor = "center")
            self.simulateButton.configure(state = "normal")

    def pauseSim(self):
        self.pauseButton.place_forget() # update the buttons and the paused variable
        self.autoButton.place(x = 140, rely = 0.5, anchor = "center")
        self.simulateButton.configure(state = "normal")
        self.paused = True
    
    def getFont(self, string):
        if len(string) > 20:
            return 10
        else:
            return 13

class RecordsMenu(ctk.CTkFrame):
    def __init__(self, parent, divisionMenu, name):
        super().__init__(parent)
        self.pack(expand = True, fill = "both")
        self.parent = divisionMenu
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

class SeasonsMenu(ctk.CTkScrollableFrame):
    def __init__(self, parent, leagueMenu, name):
        super().__init__(parent, fg_color = GRAY, scrollbar_button_color = DARK_GRAY)
        self.parent = parent
        self.leagueMenu = leagueMenu
        self.name = name
        self.season = 0
        self.positionsData = {}
        self.pointsData = {}
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
        self.tableFrame.pack(expand = True, fill = "both", pady = (0,5))
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

        relegationsNum = self.leagueMenu.numPromotions

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
            numLabel = ctk.CTkLabel(self.tableFrame, text = i + 1, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13))
            numLabel.grid(row = i + 1, column = 0)

            if i >= len(data) - relegationsNum:
                src = Image.open("Images/relCircle.png")
                img = ctk.CTkImage(src, None, (15, 15))
                numLabel.configure(image = img)

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

class GraphsMenu(ctk.CTkFrame):
    def __init__(self, parent, numTeams, name, divisionsMenu):
        super().__init__(parent, fg_color = APP_BACKGROUND)
        self.numTeams = numTeams
        self.name = name
        self.parent = divisionsMenu
        self.imgs = []  # Create a list to store all the images
        self.graph = "positions"

        self.canvasWidth = 433
        self.canvasHeight = 640
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

    def changeGraph(self, titleLabel = None, buttonlabel = None):
        if self.graph == "positions":
            self.graph = "points"
            self.changeButton.configure(text = "Positions")
            self.titleLabel.configure(text = "Points")
            self.addGraph(season = self.season, positions = self.positions, points = self.points)

            if titleLabel is not None:
                titleLabel.configure(text = "Points")
                buttonlabel.configure(text = "Positions")

        else:
            self.graph = "positions"
            self.changeButton.configure(text = "Points")
            self.titleLabel.configure(text = "Positions")
            self.addGraph(season = self.season, positions = self.positions, points = self.points)

            if titleLabel is not None:
                titleLabel.configure(text = "Positions")
                buttonlabel.configure(text = "Points")

    def addGraph(self, first = False, season = False, positions = None, points = None, logos = None):
        self.season = season
        
        if self.season:
            self.canvasParent = self.parent.seasonsMenu.graphFrame
            self.positions = positions
            self.points = points
        else:
            self.canvasParent = self.canvasFrame
            self.pack(expand = True, fill = "both")
            self.positions = self.parent.matchesMenu.positions["1"]
            self.points = self.parent.matchesMenu.points["1"]

        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)
        except:
            data = []

        if first:
            for league in data:
                if league["name"] == self.name:
                    if league["divisions"][0]["teams"] != []:
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
                
                self.canvas.delete()
                self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
                self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")
                self.drawGrid(lastMatchDay - 1)

                for i, team in enumerate(self.positions):
                    src = "SavedImages/Teams/" + team + ".png"
                    self.addPoints(self.positions[team], src, lastMatchDay - 1, i)

            else:
                mostPoints = max(x[-1] for x in self.points.values())
                self.rows = int(mostPoints)

                self.canvas.delete()
                self.canvas = ctk.CTkCanvas(self.canvasParent, bg = GRAY, width = self.canvasWidth, height = self.canvasHeight, highlightthickness = 0)
                self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")
                self.drawGrid(lastMatchDay - 1)

                for i, team in enumerate(self.points):
                    src = "SavedImages/Teams/" + team + ".png"
                    self.addPoints(self.points[team], src, lastMatchDay - 1, i)

        else:
            if self.graph == "positions":
                self.rows = self.numTeams - 1
            else:
                self.rows = 3

            self.canvas.delete()
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
                firstDivision = league["divisions"][0]
                topScorers = firstDivision["topScorer"]
                topAssisters = firstDivision["topAssister"]
                topAverageRatings = firstDivision["topAverageRating"]
                topCleanSheets = firstDivision["topCleanSheet"]
                topPens = firstDivision["topPen"]
                topPOTM = firstDivision["topPOTM"]
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





