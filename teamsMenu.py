import customtkinter as ctk
from settings import *
import json
from PIL import Image
from playerMenu import PlayerMenu

# Class that oversees the menu for a team
class TeamInfo(ctk.CTkTabview):
    def __init__(self, parent, mainMenu, name, logo):
        super().__init__(parent, height = 375, width = 300)  

        self.add("Team")
        self.add("Players")
        self.add("Records")
        self.mainMenu = mainMenu
        self.parent = parent
        self.name = name

        self.teamFrame = Team(self.tab("Team"), self.name)
        self.playersFrame = Players(self.tab("Players"), self.name, self, parent)
        self.recordsFrame = Records(self.tab("Records"), self.name)

        self.backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBack())
        self.backButton.place(x = 10, y = 10, anchor = "nw")

    def goBack(self):
        self.mainMenu.pack(expand = True, fill = "both")
        self.place_forget()

    def updateData(self, name):
        self.teamFrame.name = name
        self.name = name
        self.playersFrame.name = name
        self.recordsFrame.name = name

# Class that oversees the info of the team
class Team(ctk.CTkFrame):
    def __init__(self, parent, name):
        super().__init__(parent, fg_color = ORANGE_BG)
        self.pack(expand = True, fill = "both")
        self.name = name
    
    def addData(self):

        try:
            with open("teams.json") as file:
                teams = json.load(file)
        except:
            teams = []

        competitionsFrame = ctk.CTkScrollableFrame(self, width = 245, bg_color = DARK_GRAY, fg_color = DARK_GRAY)
        competitionsFrame.place(x = 10, y = 100, anchor = "nw")

        # look for the team's competitions and add them to the frame
        for team in teams:
            if team["name"] == self.name:
                level = team["level"]
                for comp in team["competitions"]:
                    ctk.CTkLabel(competitionsFrame, text = comp, font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))

        # add the team's information
        logo = ctk.CTkImage(Image.open("SavedImages/Teams/" + self.name + ".png"), None, (50, 50))
        self.logoLabel = ctk.CTkLabel(self, text = "", image = logo, fg_color = ORANGE_BG, text_color = "black")
        self.logoLabel.place(x = 10, y = 10, anchor = "nw")
        self.nameLabel = ctk.CTkLabel(self, text = self.name, font = (APP_FONT_BOLD, 20), fg_color = ORANGE_BG, text_color = "black")
        self.nameLabel.place(x = 70, y = 10, anchor = "nw")

        ctk.CTkLabel(self, text = "Level: " + str(level), font = (APP_FONT, 15), fg_color = ORANGE_BG, text_color = "black").place(x = 70, y = 35, anchor = "nw")

        ctk.CTkLabel(self, text = "Competitions:", font = (APP_FONT, 15), fg_color = ORANGE_BG, text_color = "black").place(x = 10, y = 70, anchor = "nw")

# Class that oversees the players of the team
class Players(ctk.CTkFrame):
    def __init__(self, parent, name, teamMenu, root):
        super().__init__(parent, fg_color = ORANGE_BG)
        self.pack(expand = True, fill = "both")

        self.name = name
        self.teamMenu = teamMenu
        self.root = root
    
    def addPlayers(self):
        try:
            with open("players.json") as file:
                teams = json.load(file)
        except:
            teams = []

        playersFrame = ctk.CTkScrollableFrame(self, height = 290, width = 245, bg_color = DARK_GRAY, fg_color = DARK_GRAY)
        playersFrame.place(x = 10, y = 10, anchor = "nw")

        for team in teams:
            if team["name"] == self.name:
                players = team["players"]
                break
        
        startingPosition = "goalkeeper"

        ctk.CTkLabel(playersFrame, text = "Goalkeepers", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
        for i, player in enumerate(players):
            if player["position"] != startingPosition:
                ctk.CTkLabel(playersFrame, text = player["position"][:1].upper() + player["position"][1:] + "s", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
                startingPosition = player["position"]
            
            noBan = True
            for ban in player["matchBan"]:
                if ban["ban"] != 0:
                    noBan = False
                    frame = ctk.CTkFrame(playersFrame, fg_color = GRAY, corner_radius = 0, height = 28)
                    frame.pack(expand = True, fill = "both", pady = (0, 3))
                    frame.grid_columnconfigure(0, weight = 3)
                    frame.grid_columnconfigure(1, weight = 1)
                    frame.grid_columnconfigure(2, weight = 1)
                    frame.grid_rowconfigure(0, weight = 1)
                    frame.grid_propagate(False)
                    
                    playerLabel = ctk.CTkLabel(frame, text = player["name"], font = (APP_FONT, 12), fg_color = GRAY, text_color = "black", height = 10)
                    playerLabel.grid(row = 0, column = 0)

                    ctk.CTkLabel(frame, text = str(ban["ban"]) + " match(es)", font = (APP_FONT, 12), fg_color = GRAY, text_color = "black", height = 10).grid(row = 0, column = 2)

                    if ban["banType"] == "red":
                        src = Image.open("Images/redCard.png")
                        img = ctk.CTkImage(src, None, (10, 10))
                    
                    elif ban["banType"] == "injury":
                        src = Image.open("Images/injury.png")
                        img = ctk.CTkImage(src, None, (10, 10))

                    ctk.CTkLabel(frame, text = "", image = img, height = 10).grid(row = 0, column = 1)
                    
                    frame.bind("<Enter> <Button-1>", lambda event, name = player["name"], team = self.name, playerLabel = playerLabel, index = i: self.openPlayerMenu(event, name, team, playerLabel, index + 1))

            if noBan:
                playerLabel = ctk.CTkLabel(playersFrame, text = player["name"], font = (APP_FONT, 12), fg_color = GRAY, text_color = "black")
                playerLabel.pack(expand = True, fill = "both", pady = (0, 3))

            playerLabel.bind("<Enter> <Button-1>", lambda event, name = player["name"], team = self.name, playerLabel = playerLabel, index = i: self.openPlayerMenu(event, name, team, playerLabel, index + 1))

    def openPlayerMenu(self, event, name, team, playerLabel, index):
        self.teamMenu.place_forget()

        if not (hasattr(playerLabel, "playerMenu")):
            playerLabel.playerMenu = PlayerMenu(self.root, self.teamMenu, name, team, playerLabel)

        playerLabel.playerMenu.place(x = 0, y = 0, anchor = "nw")
        playerLabel.playerMenu.importData(index)

# Class that oversees the records of a team
class Records(ctk.CTkFrame):
    def __init__(self, parent, name):
        super().__init__(parent, fg_color = ORANGE_BG)
        self.pack(expand = True, fill = "both")
        self.name = name
    
    def addRecords(self):

        try:
            with open("teams.json") as file:
                teams = json.load(file)

            with open("leaguesData.json") as file:
                leaguesData = json.load(file)

        except:
            teams = []
            leaguesData = []

        recordFrame = ctk.CTkScrollableFrame(self, height = 290, width = 245, bg_color = DARK_GRAY, fg_color = DARK_GRAY)
        recordFrame.place(x = 10, y = 10, anchor = "nw")

        # for each of every team's competitions, add the records
        for team in teams:
            if team["name"] == self.name:
                competitions = team["competitions"]
        
                for comp in competitions:
                    competitonFrame = ctk.CTkFrame(recordFrame, fg_color = GRAY)
                    competitonFrame.pack(expand = True, fill = "both", pady = (0, 5))

                    competitonFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight = 1)

                    ctk.CTkLabel(competitonFrame, text = comp + ":", font = (APP_FONT_BOLD, 15), fg_color = GRAY, text_color = "black").grid(row = 0, column = 0, padx = 5, sticky = "w")

                    # find the team's records in the competition's data
                    for league in leaguesData:
                        if league["name"] == comp:
                            if "divisions" not in league:
                                for team in league["teams"]:
                                    if team["name"] == self.name:
                                        records = team["seasonRecords"]
                            else:
                                for div in league["divisions"]:
                                    for team in div["teams"]:
                                        if team["name"] == self.name:
                                            records = team["seasonRecords"]

                            ctk.CTkLabel(competitonFrame, text = "- Matches won: " + str(records["won"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 1, column = 0, sticky = "w", padx = 5)
                            ctk.CTkLabel(competitonFrame, text = "- Matches drawn: " + str(records["drawn"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 2, column = 0, sticky = "w", padx = 5)
                            ctk.CTkLabel(competitonFrame, text = "- Matches lost: "  + str(records["lost"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 3, column = 0, sticky = "w", padx = 5)
                            ctk.CTkLabel(competitonFrame, text = "- Goals scored: " + str(records["goalsScored"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 4, column = 0, sticky = "w", padx = 5)
                            ctk.CTkLabel(competitonFrame, text = "- Goals conceded: " + str(records["goalsConceded"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 5, column = 0, sticky = "w", padx = 5)
                            ctk.CTkLabel(competitonFrame, text = "- Champions: " + str(records["timesWon"]), font = (APP_FONT, 12), fg_color = GRAY, text_color = "black").grid(row = 6, column = 0, sticky = "w", padx = 5, pady = (0, 5))