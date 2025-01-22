import customtkinter as ctk
from settings import *
import json, re, os, shutil
from PIL import Image
from os.path import exists
from tkinter import filedialog

class PlayerMenu(ctk.CTkTabview):
    def __init__(self, parent, teamMenu, name, team, label):
        super().__init__(parent, width = 400, height = 700)  

        self.add("Player")
        self.add("Matches")
        self.add("Stats")
        self.teamMenu = teamMenu
        self.name = name
        self.team = team

        self.playerFrame = Player(self.tab("Player"), name, team, self, label)
        self.matchesFrame = Matches(self.tab("Matches"), name, team, self)
        self.statsFrame = Stats(self.tab("Stats"), name, team)

        self.backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBack())
        self.backButton.place(x = 10, y = 10, anchor = "nw")

    def goBack(self):
        self.teamMenu.place(x = 200, y = 350, anchor = "center")
        self.place_forget()

    def importData(self, index):
        self.playerFrame.addData(index)
        self.matchesFrame.addData()
        self.statsFrame.addData()

class Player(ctk.CTkFrame):
    def __init__(self, parent, name, team, playerMenu, label):
        super().__init__(parent, fg_color = GRAY)
        self.pack(expand = True, fill = "both")
        self.name = name
        self.team = team
        self.parent = playerMenu
        self.logoImage = None
        self.playerLabel = label

    def addData(self, index):

        if os.path.exists("SavedImages/Players/" + self.team + "_" + str(index) + ".png"):
            src = Image.open("SavedImages/Players/" + self.team + "_" + str(index) + ".png")
            self.logoImage = ctk.CTkImage(src, None, (50, 50))
        else:
            src = Image.open("Images/user.png")

        user = ctk.CTkImage(src, None, (75, 75))
        ctk.CTkLabel(self, text = "", image = user).place(x = 15, y = 15, anchor = "nw")

        ctk.CTkLabel(self, text = self.name.upper(), font = (APP_FONT_BOLD, self.getFont(self.name)), text_color = "black", fg_color = GRAY).place(x = 110, y = 25, anchor = "nw")
        src = Image.open("SavedImages/Teams/" + self.team + ".png")
        team = ctk.CTkImage(src, None, (30, 30))
        ctk.CTkLabel(self, text = "", image = team).place(x = 110, y = 60, anchor = "nw")
        ctk.CTkLabel(self, text = self.team, font = (APP_FONT, 15), text_color = "black", fg_color = GRAY).place(x = 147, y = 61, anchor = "nw")

        infoFrame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 365, height = 110)
        infoFrame.place(x = 10, y = 110, anchor = "nw")

        try:
            with open("players.json", "r") as f:
                teams = json.load(f)
        except:
            teams = []

        for team in teams:
            if team["name"] == self.team:
                for player in team["players"]:
                    if player["name"] == self.name:
                        ctk.CTkLabel(infoFrame, text = player["age"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 50, y = 20, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Age", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 50, y = 40, anchor = "center")

                        ctk.CTkLabel(infoFrame, text = player["number"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 180, y = 20, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Number", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 180, y = 40, anchor = "center")

                        src = Image.open("Images/Countries/" + player["nationality"].lower() + ".png")
                        ctk.CTkLabel(infoFrame, text = "", image = ctk.CTkImage(src, None, (30, 20)), fg_color = DARK_GRAY).place(x = 310, y = 20, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Nationality", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 310, y = 40, anchor = "center")

                        ctk.CTkLabel(infoFrame, text = self.getPosition(player["position"]), font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 50, y = 70, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Position", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 50, y = 90, anchor = "center")

                        ctk.CTkLabel(infoFrame, text = player["startingChance"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 180, y = 70, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Starting chance", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 180, y = 90, anchor = "center")

                        if player["seasonStats"] != []:
                            self.seasonFrames = [None] * len(player["seasonStats"])

                            rating = 0
                            counter = 0
                            for stats in player["seasonStats"]:
                                counter += 1
                                rating += stats["averageRating"]

                                if stats["averageRating"] == 0.0:
                                    counter -= 1
            
                            if counter != 0:
                                text = str(round((rating / counter), 2))
                                foreground = self.getColor(float(text))
                            else:
                                text = "- -"
                                foreground = DARK_GRAY

                            self.numComps = len(player["seasonStats"])
                        
                        else:
                            text = "- -"
                            self.seasonFrames = None
                            foreground = DARK_GRAY

                        ctk.CTkLabel(infoFrame, text = text, font = (APP_FONT, 15), text_color = "white", fg_color = foreground, height = 20, corner_radius = 5, width = 20).place(x = 310, y = 70, anchor = "center")
                        ctk.CTkLabel(infoFrame, text = "Season rating", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY, height = 10).place(x = 310, y = 90, anchor = "center")

                        if self.seasonFrames == None:
                            seasonFrame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 365, height = 90)
                            seasonFrame.place(x = 10, y = 225, anchor = "nw")
                            ctk.CTkLabel(seasonFrame, text = self.team + " isn't in any competition", font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 180, y = 45, anchor = "center")
                        else:
                            if len(self.seasonFrames) == 1:
                                seasonFrame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 365, height = 90)
                                seasonFrame.place(x = 10, y = 225, anchor = "nw")

                                self.addSeasonData(0, player, seasonFrame)

                            else:
                                for i in range(len(self.seasonFrames)):
                                    frame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 365, height = 90)
                                    self.seasonFrames[i] = frame
                                    self.activeFrame = 0
                                    self.leftArrow = ctk.CTkButton(self, text = "<", fg_color = GRAY, bg_color = DARK_GRAY, width = 15, height = 15, corner_radius = 5, command = lambda: self.changeFrame(-1))
                                    self.leftArrow.place(x = 25, y = 240, anchor = "center")

                                    self.rightArrow = ctk.CTkButton(self, text = ">", fg_color = GRAY, width = 15, bg_color = DARK_GRAY, height = 15, corner_radius = 5, command = lambda: self.changeFrame(1))
                                    self.rightArrow.place(x = 360, y = 240, anchor = "center")

                                    self.addSeasonData(i, player, frame)
                                
                                self.seasonFrames[0].place(x = 10, y = 225, anchor = "nw")

                        # Trophies
                        trophyLabel = ctk.CTkLabel(self, text = "Trophies", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = DARK_GRAY, width = 365, height = 30, corner_radius = 5)
                        trophyLabel.place(x = 10, y = 320, anchor = "nw")

                        trophiesFrame = ctk.CTkScrollableFrame(self, fg_color = DARK_GRAY, width = 342, height = 240)
                        trophiesFrame.place(x = 10, y = 353, anchor = "nw")

                        trophiesFrame.grid_columnconfigure((0, 2), weight = 1, uniform = "a")
                        trophiesFrame.grid_columnconfigure(1, weight = 5, uniform = "a")

                        for i, comp in enumerate(player["trophies"]):
                            compIsLeague = exists("SavedImages/Leagues/" + comp + ".png")
                            compIsCup = exists("SavedImages/Cups/" + comp + ".png")
                            
                            if compIsLeague or compIsCup:
                                if compIsLeague:
                                    src = Image.open("SavedImages/Leagues/" + comp + ".png")
                                if compIsCup:
                                    src = Image.open("SavedImages/Cups/" + comp + ".png")
                            else:
                                continue
            
                            logo = ctk.CTkImage(src, None, (30, 30))
                            ctk.CTkLabel(trophiesFrame, text = "", image = logo).grid(row = i, column = 0, sticky = "w", padx = 5, pady = 5)

                            ctk.CTkLabel(trophiesFrame, text = comp, font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).grid(row = i, column = 1, sticky = "w", padx = 10, pady = 5)
                            ctk.CTkLabel(trophiesFrame, text = player["trophies"][comp], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).grid(row = i, column = 1, sticky = "e", pady = 5)

                        editButton = ctk.CTkButton(self, text = "Edit", font = (APP_FONT, 15), fg_color = ORANGE_BG, corner_radius = 5, width = 365, height = 30, command = lambda age = player["age"], num = player["number"], nat = player["nationality"]: self.editPlayer(self.team, self.name, age, num, nat.lower(), index))
                        editButton.place(x = 10, y = 610)

    def editPlayer(self, teamName, name, age, number, nat, playerIndex):
        playerFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 690, width = 391)
        playerFrame.place(x = 5, y = 5)

        logoFrame = ctk.CTkFrame(playerFrame, fg_color = GRAY, border_color = DARK_GRAY, border_width = 3, width = 75, height = 75)
        logoFrame.place(x = 15, y = 15, anchor = "nw")

        src = Image.open("Images/upload.png")
        uploadImage = ctk.CTkImage(src, None, (25, 25))

        logoButton = ctk.CTkButton(logoFrame, text = "", image = uploadImage, font = (APP_FONT_BOLD, 7), fg_color = DARK_GRAY, text_color = "black", width = 25, corner_radius = 5, command = lambda: self.chooseLogo(playerFrame, logoFrame))
        logoButton.place(relx = 0.5, rely = 0.5, anchor = "center")
        logoFrame.pack_propagate(False)

        if self.logoImage != None:
            logo = ctk.CTkLabel(logoFrame, image = self.logoImage, text = "")
            logo.pack(expand = True, fill = "both")

            Xbutton = ctk.CTkButton(playerFrame, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logo, Xbutton))
            Xbutton.place(x = 75, y = 65, anchor = "nw")

        nameEntry = ctk.CTkEntry(playerFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 200, border_color = DARK_GRAY)
        nameEntry.place(x = 110, y = 25, anchor = "nw")
        nameEntry.insert(0, name)

        src = Image.open("SavedImages/Teams/" + teamName + ".png")
        team = ctk.CTkImage(src, None, (30, 30))
        ctk.CTkLabel(playerFrame, text = "", image = team).place(x = 110, y = 60, anchor = "nw")
        ctk.CTkLabel(playerFrame, text = teamName, font = (APP_FONT, 15), text_color = "black", fg_color = GRAY).place(x = 147, y = 61, anchor = "nw")

        ageFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 382, height = 50)
        ageFrame.place(x = 5, y = 120, anchor = "nw")
        ageNum = ctk.IntVar(value = 18)
        ctk.CTkLabel(ageFrame, text = "Age:", font = (APP_FONT, 20), text_color = "white").place(x = 10, y = 10, anchor = "nw")
        ageLabel = ctk.CTkLabel(ageFrame, text = str(age), font = (APP_FONT, 20), text_color = "white")
        ageLabel.place(x = 330, y = 10, anchor = "nw")
        ageSlider = ctk.CTkSlider(ageFrame, from_ = 16, to = 45, width = 205, height = 23, fg_color = GRAY, button_color = "white", button_hover_color = "white", variable = ageNum, command = lambda value: self.printLabel(ageNum, ageLabel))
        ageSlider.set(age)
        ageSlider.place(x = 105, y = 15, anchor = "nw")

        numberFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 382, height = 50)
        numberFrame.place(x = 5, y = 175, anchor = "nw")
        numberNum = ctk.IntVar(value = 0)
        ctk.CTkLabel(numberFrame, text = "Number:", font = (APP_FONT, 20), text_color = "white", width = 10).place(x = 10, y = 10, anchor = "nw")
        numberLabel = ctk.CTkLabel(numberFrame, text = str(number), font = (APP_FONT, 20), text_color = "white")
        numberLabel.place(x = 330, y = 10, anchor = "nw")
        numberSlider = ctk.CTkSlider(numberFrame, from_ = 0, to = 99, width = 205, height = 23, fg_color = GRAY, button_color = "white", button_hover_color = "white", variable = numberNum, command = lambda value: self.printLabel(numberNum, numberLabel))
        numberSlider.set(number)
        numberSlider.place(x = 105, y = 15, anchor = "nw")

        nationalityFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 382, height = 400)
        nationalityFrame.place(x = 5, y = 230, anchor = "nw")   
        nationalityFrame.grid_rowconfigure(0, weight = 2, uniform = "a")
        nationalityFrame.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), weight = 1, uniform = "a")
        nationalityFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight = 1, uniform = "a")
        nationalityFrame.grid_propagate(False)

        ctk.CTkLabel(nationalityFrame, text = "Nationality", font = (APP_FONT, 20), text_color = "white").grid(row = 0, column = 0, columnspan = 3, sticky = "w", padx = 10)
        self.nationalityVar = ctk.StringVar(value = nat)
        src = Image.open("Images/Countries/" + nat + ".png")
        img = ctk.CTkImage(src, None, (30, 30))
        self.natImage = ctk.CTkLabel(nationalityFrame, text = "", image = img)
        self.natImage.grid(row = 0, column = 5)

        countries = os.listdir("Images/Countries")

        for i, country in enumerate(countries):
            src = Image.open("Images/Countries/" + country)
            img = ctk.CTkImage(src, None, (30, 30))

            row = i // 6 + 1
            column = i % 6

            button = ctk.CTkButton(nationalityFrame, text = "", image = img, hover_color = DARK_GRAY, fg_color = DARK_GRAY, width = 20, command = lambda country = country: self.changeCountry(country))
            button.grid(row = row, column = column)
        
        doneButton = ctk.CTkButton(playerFrame, text = "Done", font = (APP_FONT, 15), fg_color = ORANGE_BG, text_color = "black", corner_radius = 5, height = 30, width = 382, command = lambda: self.finishEdit(playerFrame, nameEntry, ageNum, numberNum, teamName, playerIndex, self.name))
        doneButton.place(x = 5, y = 645, anchor = "nw")

    def printLabel(self, var, label):
        label.configure(text = str(var.get()))

    def changeCountry(self, countryFile):
        src = Image.open("Images/Countries/" + countryFile)
        img = ctk.CTkImage(src, None, (30, 30))
        self.natImage.configure(image = img)
        self.nationalityVar.set(os.path.splitext(countryFile)[0])

    def chooseLogo(self, parent, logoFrame):
        self.file = filedialog.askopenfilename(initialdir = "Images", title = "Select a logo", filetypes = (("png files", "*.png"), ("all files", "*.*"))) # get the file using a file dialog

        if(self.file): # get rid of errors if the user doesnt select an image
            src = Image.open(self.file)

            self.logoImage = ctk.CTkImage(src, None, (50, 50))
            logo = ctk.CTkLabel(logoFrame, image = self.logoImage, text = "")
            logo.pack(expand = True, fill = "both")

            # this button will allow the user to delete the logo if they want to and choose another one
            Xbutton = ctk.CTkButton(parent, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logo, Xbutton))
            Xbutton.place(x = 75, y = 65, anchor = "nw")

    def deleteLogo(self, logo, Xbutton):
        # this function will delete the logo and allow the user to choose another
        logo.pack_forget()
        Xbutton.place_forget()

        self.logoImage = None

    def finishEdit(self, frame, nameEntry, ageNum, numberNum, teamName, index, oldName):
        # checking name
        name = nameEntry.get()
        if name == "" or len(name) > 25:
            nameEntry.configure(border_color = "red")
            return

        # add player data to the team's players list
        age = ageNum.get()
        number = numberNum.get()
        nationality = self.nationalityVar.get()

        try:
            with open("players.json", "r") as file:
                teams = json.load(file)
            with open("leaguesData.json", "r") as file:
                data = json.load(file)
        except:
            teams = []
            data = []

        for team in teams:
            if team["name"] == teamName:
                for player in team["players"]:
                    if player["name"] == oldName:
                        player["name"] = name
                        player["age"] = age
                        player["nationality"] = nationality.capitalize()
                        player["number"] = number

        if self.logoImage != None:
            try:
                shutil.copy(self.file, os.path.join("SavedImages/Players", teamName + "_" + str(index)+ ".png"))
            except:
                pass
        else:
            filePath = os.path.join("SavedImages/Players", teamName + "_" + str(index) + ".png")
            if os.path.isfile(filePath):
                os.remove(filePath)

        self.logoImage = None

        with open("players.json", "w") as file:
                json.dump(teams, file)

        self.name = name

        frame.place_forget()
        # remove the data in the player menu and re add it so that the new data is on display
        for widget in self.winfo_children():
            widget.destroy()

        self.addData(index)

        for league in data:
            for matchday in league["matchDays"]:
                for match in matchday["matches"]:
                    if match["home"] == teamName or match["away"] == teamName:
                        for scorer in match["homeScorers"]:
                            if scorer["name"] == oldName:
                                scorer["name"] = name
                            if scorer["assister"] == oldName:
                                scorer["assister"] = name
                            
                        for scorer in match["awayScorers"]:
                            if scorer["name"] == oldName:
                                scorer["name"] = name
                            if scorer["assister"] == oldName:
                                scorer["assister"] = name

                        for player in match["homeLineup"]:
                            if player["name"] == oldName:
                                player["name"] = name

                        for player in match["awayLineup"]:
                            if player["name"] == oldName:
                                player["name"] = name

                        if match["injured"] == oldName:
                            match["injured"] = name
                        
                        if match["playerOTM"] == oldName:
                            match["playerOTM"] = name

        with open("leaguesData.json", "w") as file:
            json.dump(data, file)

        self.playerLabel.configure(text = name)

    def getFont(self, str):
        if len(str) > 15:
            return 20
        if len(str) > 25:
            return 15
        
        return 25

    def addSeasonData(self, i, player, frame):
        ctk.CTkLabel(frame, text = player["seasonStats"][i]["compName"], font = (APP_FONT, 20), text_color = GRAY, fg_color = DARK_GRAY).place(x = 182, y = 15, anchor = "center")

        ctk.CTkLabel(frame, text = player["seasonStats"][i]["played"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 50, y = 45, anchor = "center")
        ctk.CTkLabel(frame, text = "Played", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 50, y = 65, anchor = "center")

        if player["position"] != "goalkeeper":
            ctk.CTkLabel(frame, text = player["seasonStats"][i]["goals"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 140, y = 45, anchor = "center")
            ctk.CTkLabel(frame, text = "Goals", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 140, y = 65, anchor = "center")

            ctk.CTkLabel(frame, text = player["seasonStats"][i]["assists"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 220, y = 45, anchor = "center")
            ctk.CTkLabel(frame, text = "Assists", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 220, y = 65, anchor = "center")
        
        else:
            ctk.CTkLabel(frame, text = player["seasonStats"][i]["clean sheets"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 140, y = 45, anchor = "center")
            ctk.CTkLabel(frame, text = "Clean sheets", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 140, y = 65, anchor = "center")

            ctk.CTkLabel(frame, text = player["seasonStats"][i]["reds"], font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GRAY).place(x = 220, y = 45, anchor = "center")
            ctk.CTkLabel(frame, text = "Red cards", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY).place(x = 220, y = 65, anchor = "center")

        if player["seasonStats"][i]["played"] == 0:
            rating = "- -"
            foreground = DARK_GRAY
        else:
            rating = player["seasonStats"][i]["averageRating"]
            foreground = self.getColor(float(rating))

        ctk.CTkLabel(frame, text = rating, font = (APP_FONT, 15), text_color = "white", fg_color = foreground, height = 20, width = 20, corner_radius = 5).place(x = 310, y = 45, anchor = "center")
        ctk.CTkLabel(frame, text = "Rating", font = (APP_FONT, 10), text_color = GRAY, fg_color = DARK_GRAY, height = 10).place(x = 310, y = 65, anchor = "center")

    def getColor(self, rating):
        if rating < 4.00:
            return BAD_RED
        elif rating < 7.00:
            return AVERAGE_ORANGE
        else:
            return GOOD_GREEN

    def getPosition(self, pos):
        if pos == "goalkeeper":
            return "GK"
        elif pos == "defender":
            return "DF"
        elif pos == "midfielder":
            return "MF"
        else:
            return "FW"
        
    def changeFrame(self, direction):
        self.seasonFrames[self.activeFrame].place_forget() 
        if self.activeFrame + direction == self.numComps:
            self.seasonFrames[0].place(x = 10, y = 225, anchor = "nw")
            self.activeFrame = 0 
        else:
            self.seasonFrames[self.activeFrame + direction].place(x = 10, y = 225, anchor = "nw")
            if self.activeFrame + direction == -1:
                self.activeFrame = self.numComps - 1
            else:
                self.activeFrame = self.activeFrame + direction

class Matches(ctk.CTkScrollableFrame):
    def __init__(self, parent, name, team, playerMenu):
        super().__init__(parent, fg_color = GRAY, scrollbar_button_color = DARK_GRAY)
        self.pack(expand = True, fill = "both")

        self.name = name
        self.team = team
        self.parent = playerMenu

    def addData(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        try:
            with open("players.json", "r") as f:
                teams = json.load(f)
        except:
            teams = []

        for team in teams:
            if team["name"] == self.team:
                for player in team["players"]:
                    if player["name"] == self.name:
                        matches = player["matches"]

                        for match in matches[::-1]:
                            matchFrame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 360, height = 90)
                            matchFrame.pack(expand = True, fill = "both", pady = (0, 5))

                            src = Image.open("SavedImages/Teams/" + match["against"] + ".png")
                            awayLogo = ctk.CTkImage(src, None, (70, 70))
                            ctk.CTkLabel(matchFrame, text = "", image = awayLogo).place(x = 10, y = 10, anchor = "nw")

                            if list(match["score"].keys())[0] == self.team:
                                ctk.CTkLabel(matchFrame, text = match["against"] + " - H", fg_color = DARK_GRAY, font = (APP_FONT, 20), text_color = "white").place(x = 90, y = 20, anchor = "nw")
                            else:
                                ctk.CTkLabel(matchFrame, text = match["against"] + " - A", fg_color = DARK_GRAY, font = (APP_FONT, 20), text_color = "white").place(x = 90, y = 20, anchor = "nw")

                            ctk.CTkLabel(matchFrame, text = str(list(match["score"].items())[0][1]) + " - " + str(list(match["score"].items())[1][1]), fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = GRAY).place(x = 90, y = 45, anchor = "nw")

                            if match["rating"] < 4.00:
                                foreground = BAD_RED
                            elif match["rating"] < 7.00:
                                foreground = AVERAGE_ORANGE
                            else:
                                foreground = GOOD_GREEN

                            if match["playerOTM"] == True:
                                foreground = PLAYER_OFM_BLUE

                            ctk.CTkLabel(matchFrame, text = match["rating"], fg_color = foreground, font = (APP_FONT, 15), text_color = DARK_GRAY, corner_radius = 5, height = 25).place(x = 358, y = 60, anchor = "se")

                            ctk.CTkLabel(matchFrame, text = match["compName"], fg_color = GRAY, font = (APP_FONT, 10), text_color = DARK_GRAY, corner_radius = 5, height = 15).place(x = 358, y = 85, anchor = "se")

                            xPlaces = [305, 290, 275, 260, 245, 230, 215, 200, 185, 170]
                            data = [match["goals"], match["own goals"], match["assists"], match["red"], 1 if match["injured"] == True else 0]
                            imgs = [ctk.CTkImage(Image.open("Images/goal.png"), None, (10, 10)), ctk.CTkImage(Image.open("Images/ownGoal.png"), None, (10, 10)), ctk.CTkImage(Image.open("Images/assist.png"), None, (10, 10)), ctk.CTkImage(Image.open("Images/redCard.png"), None, (10, 10)), ctk.CTkImage(Image.open("Images/injury.png"), None, (10, 10))]

                            counter = 0
                            for i, value in enumerate(data):
                                for j in range(value):
                                    ctk.CTkLabel(matchFrame, text = "", image = imgs[i]).place(x = xPlaces[counter], y = 45, anchor = "center")
                                    counter += 1

                            for widget in matchFrame.winfo_children():
                                widget.bind("<Enter> <Button-1>", lambda event, homeName = list(match["score"].keys())[0], awayName = list(match["score"].keys())[1], compName = match["compName"]: self.openMatch(homeName, awayName, compName))

                            matchFrame.bind("<Enter> <Button-1>", lambda event, homeName = list(match["score"].keys())[0], awayName = list(match["score"].keys())[1], compName = match["compName"]: self.openMatch(homeName, awayName, compName))

    def openMatch(self, homeName, awayName, compName):
        matchInfoFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 690, width = 390)
        matchInfoFrame.place(x = 5, y = 5)

        try:
            with open("leaguesData.json", "r") as file:
                data = json.load(file)
            
            with open("leagues.json", "r") as file:
                leagues = json.load(file)
        except:
            data = []
            leagues = []

        for league in data:
            if league["name"] == compName:

                for leagueData in leagues:
                    if leagueData["name"] == compName:
                        leagueDivs = leagueData["divisions"]

                if leagueDivs == 1:
                    for matchDay in league["matchDays"]:
                        for match in matchDay["matches"]:
                            if match["home"] == homeName and match["away"] == awayName:
                                match_ = match

                else:
                    for div in league["divisions"]:
                        for matchDay in div["matchDays"]:
                            for match in matchDay["matches"]:
                                if match["home"] == homeName and match["away"] == awayName:
                                    match_ = match

                score = match_["score"]
                matchInfo = [match_["homeScorers"], match_["awayScorers"]]
                lineups = [[player["name"] for player in match_["homeLineup"]], [player["name"] for player in match_["awayLineup"]]]
                ratings = [[player["rating"] for player in match_["homeLineup"]], [player["rating"] for player in match_["awayLineup"]]]
                injuredPlayer = match_["injured"]
                referee = match_["referee"]
                time = match_["time"]
                playerOTM = match_["playerOTM"]
        
        backButton = ctk.CTkButton(matchInfoFrame, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.goBack(matchInfoFrame))
        backButton.place(x = 2, y = 2, anchor = "nw")

        homesrc = Image.open("SavedImages/Teams/" + homeName + ".png")
        homeLogo = ctk.CTkImage(homesrc, None, (50, 50))
        ctk.CTkLabel(matchInfoFrame, text = "", image = homeLogo, fg_color = GRAY).place(x = 110, y = 50, anchor = "center")
        ctk.CTkLabel(matchInfoFrame, text = homeName, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 110, y = 100, anchor = "center")

        awaysrc = Image.open("SavedImages/Teams/" + awayName + ".png")
        awayLogo = ctk.CTkImage(awaysrc, None, (50, 50))
        ctk.CTkLabel(matchInfoFrame, text = "", image = awayLogo, fg_color = GRAY).place(x = 280, y = 50, anchor = "center")
        ctk.CTkLabel(matchInfoFrame, text = awayName, fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(x = 280, y = 100, anchor = "center")

        ctk.CTkLabel(matchInfoFrame, text = "[ " + str(score) + " ]", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 25)).place(x = 195, y = 50, anchor = "center")
        
        scorersFrame = ctk.CTkFrame(matchInfoFrame, fg_color = GRAY, height = 180, width = 380)
        scorersFrame.place(x = 5, y = 115, anchor = "nw")

        xPlaces = [149, 165, 220, 235]
        yPlaces = [0, 22, 44, 66, 88, 110, 132, 154, 176]
        for j, team in enumerate(matchInfo):
            team = sorted(team, key = lambda x: int(str(x["time"]).split("+")[0]) + int(str(x["time"]).split("+")[1]) if "+" in str(x["time"]) else int(x["time"]))

            for i, scorer in enumerate(team):
                goalScorer = scorer["name"]
                type_ = scorer["type"]
                goalTime = scorer["time"]

                if type_ == "goal":
                    src = Image.open("Images/goal.png")
                elif type_ == "penalty":
                    src = Image.open("Images/penalty.png")
                elif type_ == "own goal":
                    src = Image.open("Images/ownGoal.png")
                else:
                    src = Image.open("Images/redCard.png")

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

        lineupFrame = ctk.CTkFrame(matchInfoFrame, fg_color = GRAY, height = 250, width = 380)
        lineupFrame.place(x = 5, y = 130 + yPlaces[mostGoals], anchor = "nw")
        endOfFrame = 390 + yPlaces[mostGoals]

        ctk.CTkLabel(lineupFrame, text = "Lineups", fg_color = GRAY, text_color = "black", font = (APP_FONT_BOLD, 15)).place(relx = 0.5, y = 10, anchor = "center")

        ySpaces = [30, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230]
        for i, lineup in enumerate(lineups):
            for j, name in enumerate(lineup):
                text = name

                if i == 0:
                    playerX = 80
                    ratingX = 167
                    y = ySpaces[j]
                elif i == 1:
                    playerX = 295
                    ratingX = 207
                    y = ySpaces[j]

                if text == playerOTM:
                    if text != injuredPlayer:
                        ctk.CTkLabel(lineupFrame, text = text + " *", fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")
                    else:
                        ctk.CTkLabel(lineupFrame, text = text+ " (inj) *", fg_color = GRAY, text_color = "black", font = (APP_FONT, self.getFont(text))).place(x = playerX, y = y, anchor = "center")
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

        try:
            with open("teams.json", "r") as file:
                teams = json.load(file)
        except:
            teams = []

        for team in teams:
            if team["name"] == homeName:
                stadium = team["stadium"]

        ctk.CTkLabel(matchInfoFrame, text = stadium, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 30, y = endOfFrame, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = time, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 220, y = endOfFrame, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = compName, fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 30, y = endOfFrame + 20, anchor = "nw")
        ctk.CTkLabel(matchInfoFrame, text = referee,  fg_color = GRAY, text_color = "black", font = (APP_FONT, 13)).place(x = 220, y = endOfFrame + 20, anchor = "nw")

    def goBack(self, frame):
        frame.place_forget()

    def getFont(self, string):
        if len(string) > 20:
            return 10
        else:
            return 13

class Stats(ctk.CTkScrollableFrame):
    def __init__(self, parent, name , team):
        super().__init__(parent, fg_color = GRAY, scrollbar_button_color = DARK_GRAY)
        self.pack(expand = True, fill = "both")
        self.name = name
        self.team = team

    def addData(self):
        try:
            with open("players.json", "r") as f:
                players = json.load(f)
        except:
            players = []

        for widget in self.winfo_children():
            widget.destroy()

        for team in players:
            if team["name"] == self.team:
                for player in team["players"]:
                    if player["name"] == self.name:
                        seasonsData = player["seasonsData"]
                        ySpace = 32
                        yOffset = 13
                        xSpaces = [10, 230, 260, 290, 335, 30, 65]

                        for comp in seasonsData:
                            seasonsNumber = len(comp["seasons"])
                            compFrame = ctk.CTkFrame(self, fg_color = DARK_GRAY, width = 360, height = (35 * seasonsNumber) + 30)
                            compFrame.pack(expand = True, fill = "both", pady = (0, 5))

                            ctk.CTkLabel(compFrame, text = comp["compName"], fg_color = DARK_GRAY, font = (APP_FONT, 20), text_color = "white").place(x = xSpaces[0], y = 5, anchor = "nw")

                            ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/played.png"), None, (15, 15))).place(x = xSpaces[1], y = 20, anchor = "center")
                            if player["position"] != "goalkeeper":
                                ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/goal.png"), None, (15, 15))).place(x = xSpaces[2], y = 20, anchor = "center")
                                ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/assist.png"), None, (15, 15))).place(x = xSpaces[3], y = 20, anchor = "center")

                            else:
                                ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/cleanSheet.png"), None, (15, 15))).place(x = xSpaces[2], y = 20, anchor = "center")
                                ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/redCard.png"), None, (15, 15))).place(x = xSpaces[3], y = 20, anchor = "center")
                                
                            ctk.CTkLabel(compFrame, text = "", image = ctk.CTkImage(Image.open("Images/star.png"), None, (15, 15))).place(x = xSpaces[4], y = 20, anchor = "center")
                            
                            for i in range(seasonsNumber):
                                ctk.CTkLabel(compFrame, text = i + 1, fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[0], y = (i + 1) * ySpace, anchor = "nw")

                                src = Image.open("SavedImages/Teams/" + self.team + ".png")
                                img = ctk.CTkImage(src, None, (20, 20))
                                ctk.CTkLabel(compFrame, text = "", image = img).place(x = xSpaces[5], y = (i + 1) * ySpace, anchor = "nw")
                                ctk.CTkLabel(compFrame, text = self.team, fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[6], y = (i + 1) * ySpace, anchor = "nw")

                                ctk.CTkLabel(compFrame, text = comp["seasons"][i]["played"], fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[1], y = ((i + 1) * ySpace) + yOffset, anchor = "center")

                                if player["position"] != "goalkeeper": 
                                    ctk.CTkLabel(compFrame, text = comp["seasons"][i]["goals"], fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[2], y = ((i + 1) * ySpace) + yOffset, anchor = "center")
                                    ctk.CTkLabel(compFrame, text = comp["seasons"][i]["assists"], fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[3], y = ((i + 1) * ySpace) + yOffset, anchor = "center")

                                else:
                                    ctk.CTkLabel(compFrame, text = comp["seasons"][i]["clean sheets"], fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[2], y = ((i + 1) * ySpace) + yOffset, anchor = "center")
                                    ctk.CTkLabel(compFrame, text = comp["seasons"][i]["reds"], fg_color = DARK_GRAY, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[3], y = ((i + 1) * ySpace) + yOffset, anchor = "center")

                                if comp["seasons"][i]["averageRating"] != 0.0:
                                    ctk.CTkLabel(compFrame, text = comp["seasons"][i]["averageRating"], fg_color = self.getColor(comp["seasons"][i]["averageRating"]), height = 20, width = 20, corner_radius = 5, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[4], y = ((i + 1) * ySpace) + yOffset, anchor = "center")
                                else:
                                    ctk.CTkLabel(compFrame, text = "- -", fg_color = DARK_GRAY, height = 20, width = 20, corner_radius = 5, font = (APP_FONT, 15), text_color = "white").place(x = xSpaces[4], y = ((i + 1) * ySpace) + yOffset, anchor = "center")

    def getColor(self, rating):
        if rating < 4.00:
            return BAD_RED
        elif rating < 7.00:
            return AVERAGE_ORANGE
        else:
            return GOOD_GREEN