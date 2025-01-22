import customtkinter as ctk
from PIL import Image
from settings import *
from tkinter import filedialog
from CTkSpinbox import *
import shutil, os, json, threading, time
from leagueMenu import *
from teamsMenu import *
from divisionsMenu import *
from CTkMessagebox import CTkMessagebox
from faker import Faker
from collections import defaultdict

# Class that oversees the main menu of the app
class MainMenu(ctk.CTkTabview):
    def __init__(self, parent, loadingScreen, loadingLabel, loadingSlider):

        super().__init__(parent)
        self.rootWindow = parent
        self.loadingProgress = 0
        self.loadingScreen = loadingScreen
        self.loadingLabel = loadingLabel
        self.loadingSlider = loadingSlider

        self.add("Tournaments")
        self.add("Teams")
        self.add("Settings")

        self.teamsMenu = TeamsMenu(self.tab("Teams"), self, self.rootWindow)
        self.tournamentsMenu = TournamentsMenu(self.tab("Tournaments"), self.teamsMenu, self.rootWindow, self)
        self.settingsMenu = SettingsMenu(self.tab("Settings"))

        # variables for the threading and its progress (to update the progress bar (loadingSlider) on the loadingScreen)
        self.event1 = threading.Event()
        self.event2 = threading.Event()
        self.progress1 = 0
        self.progress2 = 0
        self.lock = threading.Lock()

        # create the threads and start importing the tournaments and teams
        threadTournaments = threading.Thread(target = self.tournamentsMenu.importLeagues, args = (self.event1, self.updateProgress1))
        threadTeams = threading.Thread(target = self.teamsMenu.importData, args = (self.event2, self.updateProgress2))

        # start threads
        threadTournaments.start()
        threadTeams.start()

        self.monitorProgress()

        # join threads
        threadTournaments.join()
        threadTeams.join()

    def updateProgress1(self, progress):
        with self.lock:
            self.progress1 = progress

    def updateProgress2(self, progress):
        with self.lock:
            self.progress2 = progress

    def monitorProgress(self):
        while not (self.event1.is_set() and self.event2.is_set()): # loops until both events are set (events are set when they have finished)
            with self.lock: # acquire the lock before the code is executed and release the lock after
                totalProgress = round((self.progress1 + self.progress2)) # get the progress
                self.loadingSlider.set(totalProgress) # set the slider to the progress
                self.loadingLabel.configure(text = f"Starting app... {totalProgress}%") # update the label
            time.sleep(1)

        # once both events are set, set the slider and text to 100 and call the synchronizedEvent
        self.loadingSlider.set(100)
        self.loadingLabel.configure(text = "Starting app... 100%")
        time.sleep(1)
        self.synchronizedEvent()

    def synchronizedEvent(self):
        self.event1.wait() # block the calling thread until the event is set
        self.event2.wait()

        # Perform the synchronized task
        self.pack(expand = True, fill = "both", padx = 10, pady = 10) # pack the main menu
        self.loadingScreen.destroy() # destroy the loading screen and every label on it

# Class that oversees the tournaments part of the app
class TournamentsMenu(ctk.CTkFrame):
    def __init__(self, parent, teamsMenu, rootWindow, mainMenu):
        super().__init__(parent)
        self.pack(expand = True, fill = "both")

        self.logoImage = None # the logo image is a global variable as you can't return values from functions called from a button
        self.file = None # same reasoning as above
        self.teamsMenu = teamsMenu
        self.root = rootWindow
        self.parent = mainMenu

        self.grid_columnconfigure(0, weight = 1)

        # the buttonsFrame contains the add league and add cup buttons
        buttonsFrame = ctk.CTkFrame(self, fg_color = None)
        buttonsFrame.pack(pady = (5, 0))

        buttonsFrame.grid_columnconfigure(0, weight = 1)
        buttonsFrame.grid_columnconfigure(1, weight = 1)

        leagueButton = ctk.CTkButton(buttonsFrame, text = "Create new league", font = (APP_FONT_BOLD, 15), fg_color = ORANGE_BG, text_color = "black", command = lambda: self.createLeagueMenu(buttonsFrame), width = 175, corner_radius = 5)
        leagueButton.grid(row = 0, column = 0, padx = (0, 5))

        cupButton = ctk.CTkButton(buttonsFrame, text = "Create new cup", font = (APP_FONT_BOLD, 15), fg_color = ORANGE_BG, text_color = "black", command = lambda: self.createCupMenu(buttonsFrame), width = 175, corner_radius = 5)
        cupButton.grid(row = 0, column = 1, padx = (5, 0))

        # this frame will contain all the labels for each tournament
        self.tournamentsFrame = ctk.CTkScrollableFrame(self, fg_color = APP_BACKGROUND, scrollbar_button_color = GRAY, scrollbar_button_hover_color = GRAY, width = 350, height = 600)
        self.tournamentsFrame.pack()
    
    def importLeagues(self, event, progressCallback):
        try:
            with open('leagues.json', 'r') as file:
                leagues = json.load(file)

            with open('leaguesData.json', 'r') as file:
                leaguesData = json.load(file)
        except:
            leagues = []
            leaguesData = []

        leagueFrames = {} 
        for league in leagues:
            leagueFrame = ctk.CTkFrame(self.tournamentsFrame, fg_color = ORANGE_BG, width = 350) # create a frame for each league
            leagueFrame.pack(pady = 5)

            # get the data
            leagueName = league["name"]
            leagueDivisions = league["divisions"]
            teamNum = league["teams"]
            promotedNum = league["promoted"]
            src = Image.open("SavedImages/Leagues/" + leagueName + ".png")
            self.logoImage = ctk.CTkImage(src, None, (80, 80)) # update the logo image

            self.createLeague(leagueFrame, None, leagueName, leagueDivisions, teamNum, promotedNum, None, None, True) # create the league (add the data to the frame)

            # Store the league frame in the dictionary
            leagueFrames[leagueName] = leagueFrame

        # create a league menu for the league
        for i, leagueData in enumerate(leaguesData):
            for league in leagues:
                if league["name"] == leagueData["name"]: 
                    leagueFrame = leagueFrames[league["name"]] 

                    # Get the data for the current league
                    leagueName = league["name"]
                    leagueDivisions = league["divisions"]
                    teamNum = league["teams"]
                    promotedNum = league["promoted"]

                    if leagueDivisions > 1:
                        leagueFrame.leagueMenu = DivisionsMenu(self.root, self.parent, leagueName, leagueDivisions, teamNum, promotedNum, self.teamsMenu, self.root)
                    else:
                        leagueFrame.leagueMenu = LeagueMenu(self.root, self.parent, leagueName, leagueDivisions, teamNum, promotedNum, self.teamsMenu, self.root)

            progressCallback((i + 1) / len(leaguesData) * 100) # call the updateProgress function to set the progress in the loadinglabel
            time.sleep(0.1)

        event.set() # set the event once finished

    def createLeagueMenu(self, buttons):
        for button in buttons.winfo_children(): # disable the create league and cup buttons
            button.configure(state = "disabled")

        # overall frame for the create league menu
        createFrame = ctk.CTkFrame(self.tournamentsFrame, fg_color = ORANGE_BG, width = 350)
        createFrame.pack(pady = 5)

        # rest are buttons / labels / counters and entries so the user can enter the data they wish for the league
        backButton = ctk.CTkButton(createFrame, text = "X", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, height = 15, width = 15, command = lambda: self.destroyFrame(createFrame, buttons))
        backButton.place(x = 340, y = 5, anchor = "ne")

        logoFrame = ctk.CTkFrame(createFrame, fg_color = ORANGE_BG, border_color = GRAY, border_width = 3, width = 100, height = 100)
        logoFrame.place(x = 10, y = 10, anchor = "nw")

        src = Image.open("Images/upload.png")
        uploadImage = ctk.CTkImage(src, None, (35, 35))

        logoButton = ctk.CTkButton(logoFrame, text = "", image = uploadImage, font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", width = 10, corner_radius = 5, command = lambda: self.chooseLogo(createFrame, logoFrame))
        logoButton.place(relx = 0.5, rely = 0.5, anchor = "center")
        logoFrame.pack_propagate(False)

        nameLabel = ctk.CTkLabel(createFrame, text = "Name:", font = (APP_FONT_BOLD, 15), text_color = "black")
        nameLabel.place(x = 130, y = 30, anchor = "nw")

        nameEntry = ctk.CTkEntry(createFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 125)
        nameEntry.place(x = 215, y = 30, anchor = "nw")

        divisionsLabel = ctk.CTkLabel(createFrame, text = "Divisions:", font = (APP_FONT_BOLD, 15), text_color = "black")
        divisionsLabel.place(x = 130, y = 60, anchor = "nw")

        divisionsNum = ctk.IntVar(value = 1)
        divisionsCounter = CTkSpinbox(createFrame, start_value = 1, min_value = 1, max_value = 4, scroll_value = 1, variable = divisionsNum, width = 125, height = 30)
        divisionsCounter.place(x = 215, y = 60, anchor = "nw")

        teamsLabel = ctk.CTkLabel(createFrame, text = "Teams per division:", font = (APP_FONT_BOLD, 15), text_color = "black")
        teamsLabel.place(x = 10, y = 125, anchor = "nw")

        teamsNum = ctk.IntVar(value = 10)
        teamsCounter = CTkSpinbox(createFrame, start_value = 2, min_value = 2, step_value = 2, max_value = 20, scroll_value = 2, variable = teamsNum, width = 125, height = 30)
        teamsCounter.place(x = 215, y = 125, anchor = "nw")

        promotedLabel = ctk.CTkLabel(createFrame, text = "Promoted/Relegated teams:", font = (APP_FONT_BOLD, 15), text_color = "black")
        promotedLabel.place(x = 10, y = 165, anchor = "nw")

        promotedNum = ctk.IntVar(value = 2)
        promotedCounter = CTkSpinbox(createFrame, start_value = 1, min_value = 1, max_value = 5, scroll_value = 1, variable = promotedNum, width = 125, height = 30)
        promotedCounter.place(x = 215, y = 165, anchor = "nw")

        # call the create league function when the ok button is clicked
        OKButton = ctk.CTkButton(createFrame, text = "OK", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, height = 15, width = 20, command = lambda: self.createLeague(createFrame, buttons, nameEntry, divisionsNum, teamsNum, promotedNum, promotedCounter, logoFrame))
        OKButton.place(x = 290, y = 5, anchor = "nw")

    def createLeague(self, frame, buttons, name, divisions, teams, promoted, promotedCounter, logoFrame, imported = False):

        if not imported: # if the data is not imported, get the data from the entries
            # check that name isnt empty and that a logo was chosen. If not, highlight the entry and logoFrame with a red border
            if (name.get() == "" or len(name.get()) > 25 or promoted.get() >= teams.get() or promoted.get() > teams.get() / 2):
                if (name.get() == "" or len(name.get()) > 25):
                    name.configure(border_color = "red")
                else:
                    name.configure(border_color = GRAY)

                if (promoted.get() >= teams.get()) and divisions.get() == 2:
                    promotedCounter.configure(border_color = "red")
                elif (promoted.get() > teams.get() / 2) and divisions.get() > 2:
                    promotedCounter.configure(border_color = "red")
                else:
                    promotedCounter.configure(border_color = GRAY)                
                return # exit the function

            if self.logoImage == None:
                self.file = "Images/defaultTrophy.png"
                self.logoImage = ctk.CTkImage(Image.open(self.file), None, (80, 80))
            
            # check for a tournament with the same name
            for file in os.listdir("SavedImages/Leagues"):
                if (file == name.get() + ".png"):
                    name.configure(border_color = "red") # highlight the entry with a red border if found and exit the function
                    return

            # save the logo into the SavedImages folder
            shutil.copy(self.file, os.path.join("SavedImages/Leagues", name.get() + ".png"))

            # get the data
            leagueName = name.get()
            leagueDivisions = divisions.get()
            teamNum = teams.get()
            promotedNum = promoted.get()

            # destroy the labels and widgets in the frame
            for widget in frame.winfo_children():
                widget.destroy()
        
        else: # if imported, get the data from the parameters as we know the data is correct (since the league was created and checked previously)
            leagueName = name
            leagueDivisions = divisions
            teamNum = teams
            promotedNum = promoted

        # reconstruct the frame with the data
        frame.grid_columnconfigure((0, 1), weight = 1)
        frame.grid_rowconfigure(0, weight = 5)
        frame.grid_rowconfigure(1, weight = 1)
        frame.grid_rowconfigure(2, weight = 1)
        frame.grid_propagate(False)

        ctk.CTkLabel(frame, image = self.logoImage, text = "").grid(row = 0, column = 0, columnspan = 2, pady = (20, 0), padx = 10)
        
        ctk.CTkLabel(frame, text = leagueName, font = (APP_FONT_BOLD, 20), text_color = "black").grid(row = 1, column = 0, columnspan = 2, pady = 10)
        ctk.CTkLabel(frame, text = "League", font = (APP_FONT_BOLD, 15), text_color = "black").grid(row = 2, column = 0, pady = 10)

        if leagueDivisions == 1:
            ctk.CTkLabel(frame, text = str(teamNum) + " teams,\n " + str(leagueDivisions) + " division", font = (APP_FONT_BOLD, 15), text_color = "black").grid(row = 2, column = 1, pady = 10)
        else:
            ctk.CTkLabel(frame, text = str(teamNum) + " teams,\n " + str(leagueDivisions) + " divisions", font = (APP_FONT_BOLD, 15), text_color = "black").grid(row = 2, column = 1, pady = 10)

        deleteButton = ctk.CTkButton(frame, text = "Delete", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, height = 15, width = 15, command = lambda: self.deleteLeague(frame, leagueName))
        deleteButton.place(x = 335, y = 5, anchor = "ne")

        # save the league data to the leagues.json and leaguesData.json files
        self.saveLeague(leagueName, leagueDivisions, teamNum, promotedNum)
        frame.imported = False

        # create a league menu for the league, only if it doesn't already exist
        if(not hasattr(frame, "leagueMenu")):
            if leagueDivisions == 1:
                frame.leagueMenu = LeagueMenu(self.root, self.parent, leagueName, leagueDivisions, teamNum, promotedNum, self.teamsMenu, self.root)
            else:
                frame.leagueMenu = DivisionsMenu(self.root, self.parent, leagueName, leagueDivisions, teamNum, promotedNum, self.teamsMenu, self.root)

        # bind the event to all children of the frame (event to open the league menu)
        for widget in frame.winfo_children():
            if(not isinstance(widget, ctk.CTkButton)):
                widget.bind("<Enter> <Button-1>", lambda event: self.openLeagueMenu(event, frame, leagueName, teamNum))

        frame.bind("<Enter> <Button-1>", lambda event: self.openLeagueMenu(event, frame, leagueName, teamNum)) # bind it to the frame

        self.logoImage = None # reset the logo image

        if (buttons != None): # re-enable the create league and cup buttons
            for button in buttons.winfo_children():
                button.configure(state = "normal")

    def deleteLeague(self, frame, leagueName):

        # use CTkMessagebox to ask the user if they are sure they want to delete the league
        question = CTkMessagebox(title = "Delete tournament", message = "Are you sure you want to delete this tournament?", icon = "question", option_1 = "Cancel", option_2 = "Yes", button_color = ORANGE_BG, fg_color = DARK_GRAY, cancel_button_color = DARK_GRAY, justify = "center")
        response = question.get()

        if response == "Cancel": # if no, exit 
            return

        frame.destroy() # destroy the frame

        try:
            with open('leagues.json', 'r') as file:
                leagues = json.load(file)

            with open('leaguesData.json', 'r') as file:
                leaguesData = json.load(file)

            with open('players.json', 'r') as file:
                teams = json.load(file)

            with open("seasonsData.json", "r") as file:
                seasonsData = json.load(file)

            with open('teams.json', 'r') as file:
                teamsData = json.load(file)
        except:
            leagues = []
            leaguesData = []
            teams = []
            seasonsData = []

        # this loop will remove the league's logo from the folder (to allow new leagues to take the old league's name if needed)
        for i in range(len(leagues)):
            if (leagues[i]["name"] == leagueName):
                os.remove("SavedImages/Leagues/" + leagueName + ".png")
                leagues.pop(i) # remove the league from the leagues data in leagues.json
                break
        
        # this loop will remove the league from the leaguesData.json file
        for i in range(len(leaguesData)):
            if (leaguesData[i]["name"] == leagueName):
                leaguesData.pop(i)
                break

        # this loop will remove the league from any competitions entries in the players.json file
        for team in teamsData:
            for comp in team["competitions"]:
                if comp == leagueName:
                    team["competitions"].remove(leagueName)

                    for team2 in teams:
                        if team["name"] == team2["name"]:
                            for player in team2["players"]:
                                player["seasonStats"] = [data for data in player["seasonStats"] if data["compName"] != leagueName]

                                player["matches"] = [match for match in player["matches"] if match["compName"] != leagueName]

                                player["seasonsData"] = [data for data in player["seasonsData"] if data["compName"] != leagueName]

                                player["matchBan"] = [data for data in player["matchBan"] if data["compName"] != leagueName]

                                player["trophies"] = {key: value for key, value in player["trophies"].items() if key != leagueName}

        # remove the league in seasonsData
        for league in seasonsData:
            if league["name"] == leagueName:
                seasonsData.remove(league)

        with open("seasonsData.json", "w") as file:
            json.dump(seasonsData, file)

        with open('teams.json', 'w') as file:
            json.dump(teamsData, file)

        with open('players.json', 'w') as file:
            json.dump(teams, file)

        with open('leagues.json', 'w') as file:
            json.dump(leagues, file)

        with open('leaguesData.json', 'w') as file:
            json.dump(leaguesData, file)

    def createCupMenu(self, buttons):
        for button in buttons.winfo_children():
            button.configure(state = "disabled")

        createFrame = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 350)
        createFrame.pack(pady = 5)

        backButton = ctk.CTkButton(createFrame, text = "X", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, height = 15, width = 15, command = lambda: self.destroyFrame(createFrame, buttons))
        backButton.place(x = 340, y = 5, anchor = "ne")

        logoFrame = ctk.CTkFrame(createFrame, fg_color = ORANGE_BG, border_color = GRAY, border_width = 3, width = 65, height = 65)
        logoFrame.place(x = 10, y = 10, anchor = "nw")

        src = Image.open("Images/upload.png")
        uploadImage = ctk.CTkImage(src, None, (20, 20))

        logoButton = ctk.CTkButton(logoFrame, text = "", image = uploadImage, font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", width = 10, corner_radius = 5, command = lambda: self.chooseLogo(createFrame, logoFrame))
        logoButton.place(relx = 0.5, rely = 0.5, anchor = "center")
        logoFrame.pack_propagate(False)

        nameLabel = ctk.CTkLabel(createFrame, text = "Name:", font = (APP_FONT_BOLD, 15), text_color = "black")
        nameLabel.place(x = 90, y = 30, anchor = "nw")

        nameEntry = ctk.CTkEntry(createFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 125)
        nameEntry.place(x = 150, y = 30, anchor = "nw")

        groupsLabel = ctk.CTkLabel(createFrame, text = "Groups:", font = (APP_FONT_BOLD, 15), text_color = "black")
        groupsLabel.place(x = 10, y = 85, anchor = "nw")

        groupsNum = ctk.IntVar(value = 1)
        groupsCounter = CTkSpinbox(createFrame, start_value = 1, min_value = 0, max_value = 8, scroll_value = 1, variable = groupsNum, width = 150, height = 30)
        groupsCounter.place(x = 150, y = 85, anchor = "nw")

        knockoutLabel = ctk.CTkLabel(createFrame, text = "Knockout rounds:", font = (APP_FONT_BOLD, 15), text_color = "black")
        knockoutLabel.place(x = 10, y = 122, anchor = "nw")

        knockoutNum = ctk.IntVar(value = 1)
        knockoutCounter = CTkSpinbox(createFrame, start_value = 1, min_value = 0, max_value = 6, scroll_value = 1, variable = knockoutNum, width = 150, height = 30)
        knockoutCounter.place(x = 150, y = 122, anchor = "nw")

        teamsPerGroupLabel = ctk.CTkLabel(createFrame, text = "Teams per group:", font = (APP_FONT_BOLD, 15), text_color = "black")
        teamsPerGroupLabel.place(x = 10, y = 160, anchor = "nw")

        teamsPerGroupNum = ctk.IntVar(value = 4)
        teamsPerGroupCounter = CTkSpinbox(createFrame, start_value = 2, min_value = 2, step_value = 1, max_value = 12, scroll_value = 2, variable = teamsPerGroupNum, width = 150, height = 30)
        teamsPerGroupCounter.place(x = 150, y = 160, anchor = "nw")

        OKButton = ctk.CTkButton(createFrame, text = "OK", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, height = 15, width = 20, command = lambda: self.createCup(createFrame, buttons, nameEntry, groupsNum, groupsCounter, knockoutNum, knockoutCounter, teamsPerGroupNum, teamsPerGroupCounter, logoFrame))
        OKButton.place(x = 290, y = 5, anchor = "nw")

    def createCup(self, frame, buttons, name, groups, groupsCounter, knockout, knockoutCounter, teamsPerGroup, teamsPerGroupCounter, logoFrame, imported = False):
        global mainMenu

        if groups.get() != 0:
            promotedTeams = float((2 ** knockout.get()) / groups.get())
        else: 
            promotedTeams = 0.0

        if not imported:
            if (name.get() == "" or self.logoImage == None or ((groups.get() * teamsPerGroup.get()) < knockout.get()) or (not promotedTeams.is_integer()) or (groups.get() == 0 and knockout.get() == 0)):
                if name.get() == "":
                    name.configure(border_color = "red")
                else:
                    name.configure(border_color = GRAY)
                
                if self.logoImage == None:
                    logoFrame.configure(border_color = "red")
                else:
                    logoFrame.configure(border_color = GRAY)

                if (groups.get() * teamsPerGroup.get()) < (2 ** knockout.get()):
                    groupsCounter.configure(border_color = "red")
                    teamsPerGroupCounter.configure(border_color = "red")
                    knockoutCounter.configure(border_color = "red")
                elif not promotedTeams.is_integer():
                    groupsCounter.configure(border_color = "red")
                    teamsPerGroupCounter.configure(border_color = "red")
                    knockoutCounter.configure(border_color = "red")
                elif groups.get() == 0 and knockout.get() == 0:
                    groupsCounter.configure(border_color = "red")
                    teamsPerGroupCounter.configure(border_color = "red")
                    knockoutCounter.configure(border_color = "red")
                else:
                    groupsCounter.configure(border_color = GRAY)
                    teamsPerGroupCounter.configure(border_color = GRAY)
                    knockoutCounter.configure(border_color = GRAY)
                
                return

    def deleteCup(self, frame, cupName):
        pass

    def destroyFrame(self, frame, buttons):
        # this function is only called when the user presses the "X (back)" button when creating a cup or league
        frame.destroy()
        self.logoImage = None
        
        # re-enable the create league and cup buttons
        for button in buttons.winfo_children():
            button.configure(state = "normal")

    def chooseLogo(self, parent, logoFrame):
        self.file = filedialog.askopenfilename(initialdir = "Images", title = "Select a logo", filetypes = (("png files", "*.png"), ("all files", "*.*"))) # get the file using a file dialog

        if(self.file): # get rid of errors if the user doesnt select an image
            src = Image.open(self.file)
            self.logoImage = ctk.CTkImage(src, None, (80, 80))

            logo = ctk.CTkLabel(logoFrame, image = self.logoImage, text = "")
            logo.pack(expand = True, fill = "both")

            # this button will allow the user to delete the logo if they want to and choose another one
            Xbutton = ctk.CTkButton(parent, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logo, Xbutton))
            Xbutton.place(x = 110, y = 95, anchor = "nw")

    def deleteLogo(self, logo, Xbutton):
        # this function will delete the logo and allow the user to choose another
        logo.pack_forget()
        Xbutton.place_forget()
        
        self.logoImage = None

    def openLeagueMenu(self, event, frame, leagueName, teams):

        try:
            with open('leagues.json', 'r') as file:
                leagues = json.load(file)

            with open('leaguesData.json', 'r') as file:
                leaguesData = json.load(file)
        except:
            leagues = []
            leaguesData = []
        
        if not frame.imported: # this block happens only once when the league is opened for the first time
            for widget in frame.winfo_children(): # finds the label which is the team's name to then change its text for loading information
                if widget.cget("text") == leagueName:
                    loadingLabel = widget
            
            loadingLabel.configure(text = "Loading: Table")
            loadingLabel.update_idletasks()

            for leagueData in leaguesData:
                for league in leagues:
                    if league["name"] == leagueName and leagueData["name"] == leagueName :
                        if "divisions" not in leagueData: 
                            if leagueData["teams"] != []:
                                frame.leagueMenu.importData(leagueData) # import table
                        else:
                            if leagueData["divisions"][0]["teams"] != []:
                                frame.leagueMenu.importData(leagueData, league)

            loadingLabel.configure(text = "Loading: Matches")
            loadingLabel.update_idletasks()
            frame.leagueMenu.matchesMenu.importMatches() # import matches

            loadingLabel.configure(text = "Loading: Records")
            loadingLabel.update_idletasks()
            frame.leagueMenu.recordsMenu.addTeamRecords() # import records
            frame.leagueMenu.recordsMenu.addIndividualRecords()

            loadingLabel.configure(text = "Loading: Stats")
            loadingLabel.update_idletasks()
            frame.leagueMenu.statsMenu.importStats() # import stats

            loadingLabel.configure(text = "Loading: Seasons")
            loadingLabel.update_idletasks()
            frame.leagueMenu.seasonsMenu.importSeasons() # import seasons

            loadingLabel.configure(text = "Loading: Graphs")
            loadingLabel.update_idletasks()
            frame.leagueMenu.graphsMenu.addGraph(True)
            loadingLabel.configure(text = leagueName)

            frame.imported = True # no need to import data again
        
        frame.leagueMenu.matchesMenu.importBans() # only data that needs to imported every time the league is opened is the match bans
        
        self.parent.pack_forget() # remove the mainMenu so that the leagueMenu can be displayed
        frame.leagueMenu.pack(expand = True, fill = "both", padx = 10, pady = 10)
        
        try:
            with open("leaguesData.json", "r") as file:
                leaguesData = json.load(file)
        except:
            leaguesData = []

        I = 0
        for index, league in enumerate(leaguesData):
            if league["name"] == leagueName: # find the league
                I = index
                break
        
        # check if last matchday was completed, so that the "new Season" button can be enabled
        league = leaguesData[I]
        if "divisions" not in league:
            matchDays = league["matchDays"] if "matchDays" in league else []
            if (matchDays != []):
                lastMatchDay = matchDays[(teams * 2) - 3]
                if lastMatchDay["matches"][0]["played"] != 0: # only need to check one as all the matches in one matchDay are done at once
                    frame.leagueMenu.newSeasonButton.configure(state = "normal")
        else:
            div = league["divisions"][0]
            matchDays = div["matchDays"] if "matchDays" in div else []
            if (matchDays != []):
                lastMatchDay = matchDays[(teams * 2) - 3]
                if lastMatchDay["matches"][0]["played"] != 0:
                    frame.leagueMenu.newSeasonButton.configure(state = "normal")
    
    def openCupMenu(self, event, frame, cupName, groupsNum, knockoutNum, teamsPerGroup):
        pass

    def saveLeague(self, name, divisions, teams, promoted):
        try:
            with open('leagues.json', 'r') as file:
                leagues = json.load(file)

            with open('leaguesData.json', 'r') as file:
                leaguesData = json.load(file)

            with open("seasonsData.json", "r") as file:
                seasonsData = json.load(file)
        except:
            leagues = []
            leaguesData = []
            seasonsData = []

        referees = [] # create the referees for the league (same number as the number of teams)
        for i in range(teams * divisions):
            faker = Faker()
            ref = faker.name_male()

            ref = ref.replace("Mr. ", "").replace("Dr. ", "").replace(" PhD", "").replace(" MD", "").replace(" DVM", "").replace(".", "").replace(" DDS", "")
            referees.append(ref)

        # create a new league entry for the json file
        league = {
            "name": name,
            "divisions": divisions,
            "teams": teams,
            "promoted": promoted,
            "logoPath": "SavedImages/Leagues/" + name + ".png",
            "seasons": 1,
            "referees": referees,
            "teamRecords": {
                "most points": {"value": 1000, "team": "", "season": 0},
                "least points": {"value": 1000, "team": "", "season": 0},
                "most wins": {"value": 1000, "team": "", "season": 0},
                "least wins": {"value": 1000, "team": "", "season": 0},
                "most draws": {"value": 1000, "team": "", "season": 0},
                "least draws": {"value": 1000, "team": "", "season": 0},
                "most losses": {"value": 1000, "team": "", "season": 0},
                "least losses": {"value": 1000, "team": "", "season": 0},
                "most goals scored": {"value": 1000, "team": "", "season": 0},
                "least goals scored": {"value": 1000, "team": "", "season": 0},
                "most goals conceded": {"value": 1000, "team": "", "season": 0},
                "least goals conceded": {"value": 1000, "team": "", "season": 0},
                "most goal difference": {"value": 1000, "team": "", "season": 0},
                "least goal difference": {"value": 1000, "team": "", "season": 0},
                "most times won": {"value": 1000, "team": ""}
            },
            "individualRecords": {
                "most goals": {"player": "", "value": 1000, "team": "", "season": 0},
                "most hattricks": {"player": "", "value": 1000, "team": "", "season": 0},
                "most penalties": {"player": "", "value": 1000, "team": "", "season": 0},
                "most goals without penalties": {"player": "", "value": 1000, "team": "", "season": 0},
                "most goals in one game": {"player": "", "value": 1000, "team": "", "against": "", "season": 0},
                "most assists": {"player": "", "value": 1000, "team": "", "season": 0},
                "most player of the match awards": {"player": "", "value": 1000, "team": "", "season": 0},
                "most clean sheets": {"player": "", "value": 1000, "team": "", "season": 0},
                "best average rating": {"player": "", "value": 1000, "team": "", "season": 0}
            }
        }

        # check if there is a league with the same name; could be done by checking the images in the SavedImages/Leagues folder too
        duplicate = False
        for i in range(len(leagues)):
            if (leagues[i]["name"] == name):
                duplicate = True
                break
        if not duplicate:
            leagues.append(league)

        # create a new entry for the leaguesData file
        if divisions == 1:
            newEntry = {
                "name": name,
                "topScorer": [],
                "topAssister": [],
                "topAverageRating": [],
                "topCleanSheet": [],
                "topPen": [],
                "topPOTM": [],
                "teams": [],
                "matchDays": []
            }
        else:
            newEntry = {
                "name": name,
                "divisions": []
            }

            for i in range(divisions):
                if i == 0:
                    newEntry["divisions"].append({
                        "topScorer": [],
                        "topAssister": [],
                        "topAverageRating": [],
                        "topCleanSheet": [],
                        "topPen": [],
                        "topPOTM": [],
                        "teams": [],
                        "matchDays": []
                    })
                else:
                    newEntry["divisions"].append({
                        "teams": [],
                        "matchDays": []
                    })
        
        # again check that it can be added if there is no duplicate
        add = True
        for league in leaguesData:
            if (league["name"] == name):
                add = False
                break
        if add:
            leaguesData.append(newEntry)
        
        seasonsEntry = {
            "name": name,
            "winners": [],
            "tables": [],
            "positions": [],
            "points": [],
            "topScorer": [],
            "topAssister": [],
            "topAverageRating": [],
            "topCleanSheet": [],
            "topPen": [],
            "topPOTM": [],
        }

        add = True
        for league in seasonsData:
            if league["name"] == name:
                add = False
                break
        if add:
            seasonsData.append(seasonsEntry)

        with open('leaguesData.json', 'w') as file:
            json.dump(leaguesData, file)

        with open('leagues.json', 'w') as file:
            json.dump(leagues, file)

        with open("seasonsData.json", "w") as file:
            json.dump(seasonsData, file)

    def saveCup(self, name, groupsNum, knockoutNum, teamsPerGroup):
        pass

# Class that oversees the teams part of the app
class TeamsMenu(ctk.CTkFrame):
    def __init__(self, parent, mainMenu, root):
        super().__init__(parent)

        self.logoImage = None
        self.playerImage = None
        self.file = None
        self.newSeason = False
        self.levelLabels = []
        self.parent = mainMenu
        self.root = root

        self.pack(expand = True, fill = "both")

        buttonsFrame = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 350, height = 40)
        buttonsFrame.pack(pady = 5)

        # Frame that holds the create team buttons
        buttonsFrame.grid_columnconfigure((0, 1), weight = 1)
        buttonsFrame.grid_rowconfigure(0, weight = 1)
        buttonsFrame.grid_propagate(False)

        teamButton = ctk.CTkButton(buttonsFrame, text = "Create new team", font = (APP_FONT_BOLD, 15), fg_color = GRAY, text_color = "black", command = lambda: self.createTeamMenu(self, buttonsFrame), width = 160, corner_radius = 5)
        teamButton.grid(row = 0, column = 0, padx = 5)

        teamButton10 = ctk.CTkButton(buttonsFrame, text = "Create 10 teams", font = (APP_FONT_BOLD, 15), fg_color = GRAY, text_color = "black", command = lambda: self.create10Teams(self, buttonsFrame), width = 160, corner_radius = 5)
        teamButton10.grid(row = 0, column = 1, padx = 5)

        # Frame that holds the search entry, search button, reset button and the up/down scroll buttons
        self.searchFrame = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 350, height = 45)
        self.searchFrame.pack(pady = 5)
        self.searchFrame.grid_columnconfigure(0, weight = 1)
        self.searchFrame.grid_columnconfigure(1, weight = 2)
        self.searchFrame.grid_rowconfigure(0, weight = 1)
        self.searchFrame.grid_propagate(False)

        self.searchVar = ctk.StringVar()
        self.searchEntry = ctk.CTkEntry(self.searchFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 180, textvariable = self.searchVar)
        self.searchEntry.grid(row = 0, column = 0, padx = 5)

        # this frame will hold all the buttons
        buttonsFrame2 = ctk.CTkFrame(self.searchFrame, fg_color = ORANGE_BG, width = 350, height = 40)
        buttonsFrame2.grid(row = 0, column = 1, padx = 5)

        buttonsFrame2.grid_columnconfigure((0, 1, 2, 3), weight = 1)
        buttonsFrame2.grid_rowconfigure(0, weight = 1)

        src = Image.open("Images/search.png")
        self.searchButton = ctk.CTkButton(buttonsFrame2, text = "", image = ctk.CTkImage(src, None, (17, 17)) ,font = (APP_FONT_BOLD, 10), fg_color = GRAY, corner_radius = 5, width = 30, command = lambda: self.searchTeams(self.searchVar.get()))
        self.searchButton.grid(row = 0, column = 0, padx = 5)

        src = Image.open("Images/resetDisabled.png")
        self.resetButton = ctk.CTkButton(buttonsFrame2, text = "", image = ctk.CTkImage(src, None, (17, 17)), font = (APP_FONT_BOLD, 10), fg_color = GRAY,corner_radius = 5, width = 30, state = "disabled", command = lambda: self.reset())
        self.resetButton.grid(row = 0, column = 1, padx = (5, 10))

        src = Image.open("Images/up.png")
        scrollUpButton = ctk.CTkButton(buttonsFrame2, text = "", image = ctk.CTkImage(src, None, (17, 17)), font = (APP_FONT_BOLD, 10), fg_color = GRAY, corner_radius = 5, width = 25, command = lambda: self.teamsFrame._parent_canvas.yview_moveto(0))
        scrollUpButton.grid(row = 0, column = 2, padx = (10, 5))

        src = Image.open("Images/down.png")
        scrollDownButton = ctk.CTkButton(buttonsFrame2, text = "", image = ctk.CTkImage(src, None, (17, 17)), font = (APP_FONT_BOLD, 10), fg_color = GRAY, corner_radius = 5, width = 25, command = lambda: self.teamsFrame._parent_canvas.yview_moveto(1))
        scrollDownButton.grid(row = 0, column = 3, padx = 5)

        # Frame that holds the teams
        self.teamsFrame = ctk.CTkScrollableFrame(self, fg_color = APP_BACKGROUND, scrollbar_button_color = GRAY, scrollbar_button_hover_color = GRAY, width = 350, height = 510)
        self.teamsFrame.pack()
    
    def importData(self, event, progressCallback, data = []):
        def loadData(team, callback):
            # Load data and image in background thread
            teamName = team["name"]
            stadiumName = team["stadium"]
            teamLevel = team["level"]
            f = team["logoPath"]
            src = Image.open("SavedImages/Teams/" + teamName + ".png")
            logoImage = ctk.CTkImage(src, None, (50, 50))
            
            # Once data is loaded, call the callback in the main thread to update UI
            callback(teamFrame, logoImage, teamName, stadiumName, teamLevel, f)

        def updateUi(teamFrame, logoImage, teamName, stadiumName, teamLevel, f):
            # This function updates the UI with the loaded data
            # Ensure this runs in the main thread
            self.createTeam(self, teamFrame, None, teamName, stadiumName, teamLevel, None, None, False, False, True, logoImage, f)

        try:
            with open('teams.json', 'r') as file:
                teams = json.load(file)
        except:
            teams = []

        if data == []:
            teamsData = teams
        else:
            teamsData = data

        # for each team in the players.json file, create a frame for the team's data
        for i, team in enumerate(teamsData):
            teamFrame = ctk.CTkFrame(self.teamsFrame, fg_color = ORANGE_BG, width = 350, height = 75)
            teamFrame.pack(pady = 5)
            
            # Start a thread for each team to load its data
            threading.Thread(target = loadData, args = (team, lambda *args: self.after(0, updateUi, *args))).start()
            if progressCallback != None:
                progressCallback((i + 1) / len(teamsData) * 100)
                time.sleep(0.1)

        if event != None:
            event.set()

    def createTeamMenu(self, parent, buttonFrame, name = "", stadium = "", level = 1, logo = None, createFrame = None, oldName = None, first = True):
        if buttonFrame != None: # disable the create team button
            for button in buttonFrame.winfo_children():
                button.configure(state = "disabled")

        self.searchButton.configure(state = "disabled")
        src = Image.open("Images/searchDisabled.png")
        self.searchButton.configure(image = ctk.CTkImage(src, None, (17, 17)))
        
        # Unbind all events of all widgets (to prevent editing another team while editing/creating a team), events are re-binded later in the createTeam function
        for frame in parent.winfo_children():
            for widget in frame.winfo_children():
                widget.unbind("<Enter> <Button-1>")

            frame.unbind("<Enter> <Button-1>")

        if createFrame == None: # creating a team
            createFrame = ctk.CTkFrame(self.teamsFrame, fg_color = ORANGE_BG, width = 350, height = 165)
            createFrame.pack(pady = 5)
            playersCreated = False # players have not been created yet when creating a team, and serves for the state of the createPlayersCheck widget 
        else: # editing a team
            createFrame.configure(height = 165)
            playersCreated = True

        # create the buttons / labels / counters and entries so the user can enter the data they wish for the team
        backButton = ctk.CTkButton(createFrame, text = "Delete", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, height = 15, width = 15, command = lambda: self.destroyFrame(createFrame, parent, buttonFrame, oldName))
        backButton.place(x = 340, y = 160, anchor = "se")

        logoFrame = ctk.CTkFrame(createFrame, fg_color = ORANGE_BG, border_color = GRAY, border_width = 3, width = 70, height = 70)
        logoFrame.place(x = 10, y = 10, anchor = "nw")
        logoFrame.pack_propagate(False)

        src = Image.open("Images/upload.png")
        uploadImage = ctk.CTkImage(src, None, (15, 15))
        uploadButton = ctk.CTkButton(logoFrame, text = "", image = uploadImage, font = (APP_FONT_BOLD, 7), fg_color = GRAY, text_color = "black", width = 25, corner_radius = 5, command = lambda: self.chooseLogo(createFrame, logoFrame))
        uploadButton.place(relx = 0.28, rely = 0.5, anchor = "center")

        src = Image.open("Images/pencil.png")
        pencilImage = ctk.CTkImage(src, None, (15, 15))
        pencilButton = ctk.CTkButton(logoFrame, text = "", image = pencilImage, font = (APP_FONT_BOLD, 7), fg_color = GRAY, text_color = "black", width = 25, corner_radius = 5, command = lambda: self.createLogo(createFrame, logoFrame))
        pencilButton.place(relx = 0.70, rely = 0.5, anchor = "center")

        if logo != None: # if there is a logo (editing), add it
            self.logoImage = logo
            logo = ctk.CTkLabel(logoFrame, image = logo, text = "")
            logo.pack(expand = True, fill = "both")

            Xbutton = ctk.CTkButton(createFrame, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logo, Xbutton))
            Xbutton.place(x = 70, y = 65, anchor = "nw")

        nameLabel = ctk.CTkLabel(createFrame, text = "Name:", font = (APP_FONT_BOLD, 15), text_color = "black")
        nameLabel.place(x = 90, y = 10, anchor = "nw")

        nameEntry = ctk.CTkEntry(createFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 140)
        nameEntry.place(x = 150, y = 10, anchor = "nw")
        nameEntry.insert(0, name)

        levelTitle = ctk.CTkLabel(createFrame, text = "Level:", font = (APP_FONT_BOLD, 15), text_color = "black")
        levelTitle.place(x = 90, y = 40, anchor = "nw")

        levelNum = ctk.IntVar(value = 1)
        # levelLabel = ctk.CTkLabel(createFrame, text = str(level), font = (APP_FONT_BOLD, 15), text_color = "black")
        # levelLabel.place(x = 305, y = 42, anchor = "nw")
        levelEntry = ctk.CTkEntry(createFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 40)
        levelEntry.place(x = 295, y = 42, anchor = "nw")
        levelEntry.insert(0, str(level))
        levelSlider = ctk.CTkSlider(createFrame, from_ = 0, to = 200, variable = levelNum, width = 140, height = 23, fg_color = GRAY, button_color = DARK_GRAY, button_hover_color = DARK_GRAY, command = lambda value: self.changeEntryText(levelNum, levelEntry))
        levelSlider.set(int(level))
        levelSlider.place(x = 147, y = 45, anchor = "nw")

        stadiumLabel = ctk.CTkLabel(createFrame, text = "Stadium:", font = (APP_FONT_BOLD, 15), text_color = "black")
        stadiumLabel.place(x = 10, y = 85, anchor = "nw")

        stadiumEntry = ctk.CTkEntry(createFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 125)
        stadiumEntry.place(x = 85, y = 85, anchor = "nw")
        stadiumEntry.insert(0, stadium)

        createPlayersLabel = ctk.CTkLabel(createFrame, text = "Create players manually", font = (APP_FONT_BOLD, 15), text_color = "black")
        createPlayersLabel.place(x = 10, y = 125, anchor = "nw")
        createPlayersVar = ctk.BooleanVar(value = False)
        createPlayersCheck = ctk.CTkCheckBox(createFrame, text = "", variable = createPlayersVar, fg_color = ORANGE_BG, text_color = "black", width = 20)
        createPlayersCheck.place(x = 210, y = 125, anchor = "nw")

        if playersCreated == True: # add a red cross if the players have already been created, to disable the checkbox
            createPlayersCheck.destroy()
            src = Image.open("Images/redCross.png")
            redCross = ctk.CTkImage(src, None, (45, 45))
            redCrossLabel = ctk.CTkLabel(createFrame, image = redCross, text = "")
            redCrossLabel.place(x = 200, y = 115, anchor = "nw")

        # call the create team function when the ok button is clicked
        OKButton = ctk.CTkButton(createFrame, text = "OK", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, height = 15, width = 20, command = lambda: self.createTeam(parent, createFrame, buttonFrame, nameEntry, stadiumEntry, levelEntry, logoFrame, oldName, first, createPlayersVar))
        OKButton.place(x = 340, y = 5, anchor = "ne")

    def createTeam(self, parent, frame, buttonFrame, name, stadium, level, logoFrame, oldName, first, createPlayersVar, imported = False, logo = None, file = None):
        
        try: 
            with open('teams.json', 'r') as file:
                teamsData = json.load(file)
        except:
            teamsData = []

        if oldName != None: # if the team is being edited, check if it is part of a competition
            for team in teamsData:
                if team["name"] == oldName:
                    if team["competitions"] != [] and oldName != name.get():
                        CTkMessagebox(title = "Info", message = "Unable to edit team name, it is part of a competition", icon = "info", fg_color = DARK_GRAY, justify = "center")
                        return
                    break

        if logo != None:
            self.logoImage = logo
            self.file = file
        
        if not imported: # if the data wasnt imported, the parameters are entries and counters
            # get the data
            teamName = name.get()
            teamLevel = level.get()
            stadiumName = stadium.get()

            # check for a team with the same name
            for file in os.listdir("SavedImages/Teams"):
                if file == teamName + ".png" and teamName != oldName:
                    sameName = True
                    break
                else:
                    sameName = False

            # check if the name is empty or if a logo was chosen. If so, highlight the entry and logoFrame with a red border
            if teamName == "" or stadiumName == "" or len(teamName) > 25 or sameName or (not str(teamLevel).isdigit() or not (0 <= int(teamLevel) <= 200)):
                if teamName == "" or len(teamName) > 25 or sameName:
                    name.configure(border_color = "red")
                else:
                    name.configure(border_color = GRAY)

                if stadiumName == "":
                    stadium.configure(border_color = "red")
                else:
                    stadium.configure(border_color = GRAY)

                if not teamLevel.isdigit() or not (0 <= int(teamLevel) <= 200):
                    level.configure(border_color = "red")
                else:
                    level.configure(border_color = GRAY)

                return # exit the function if any of the conditions are met
            
            teamLevel = int(teamLevel)
        
            if self.logoImage == None: # set the logo image to the default logo if no logo was chosen
                self.file = "Images/defaultClub.png"
                self.logoImage = ctk.CTkImage(Image.open(self.file), None, (50, 50))

            # save the logo into the SavedImages folder
            try:
                shutil.copy(self.file, os.path.join("SavedImages/Teams", teamName + ".png"))

                if os.path.exists("Images/SampleLogos/modifiedLogoProgress.png"): # if the logo was created using the createLogo function, then delete the file that it was previously saved to
                    os.remove("Images/SampleLogos/modifiedLogoProgress.png")
            except:
                pass

            # destroy the labels and widgets in the frame, so that the new data can be added
            for widget in frame.winfo_children():
                widget.destroy()

        else: # if imported, the parameters are simply values
            teamName = name
            teamLevel = level
            stadiumName = stadium
        
        frame.configure(height = 75) # change the height of the frame
        self.fontsize = 25
        self.getFontSize(teamName) # get a suitable font size for the team name
        ctk.CTkLabel(frame, image = self.logoImage, text = "").place(x = 10, y = 10, anchor = "nw")
        ctk.CTkLabel(frame, text = teamName.upper(), font = (APP_FONT_BOLD, self.fontsize), text_color = "black").place(x = 80, y = 15, anchor = "nw")
        ctk.CTkLabel(frame, text = stadiumName, font = (APP_FONT, 12), text_color = "black").place(x = 80, y = 40, anchor = "nw")
    
        src = Image.open("Images/levelCircle.png")
        levelCircle = ctk.CTkImage(src, None, (50, 50))
        levelLabel = ctk.CTkLabel(frame, text = teamLevel, image = levelCircle, font = (APP_FONT_BOLD, 15), text_color = "black")
        levelLabel.place(x = 330, y = 12, anchor = "ne")
        self.levelLabels.append([name, levelLabel]) # add the label to a list so that it can be changed later (after a season)

        logo = self.logoImage

        if not hasattr(frame, "teamInfo"): # if the team does not have a teamInfo frame, create one
            frame.teamInfo = TeamInfo(self.root, self.parent, teamName, logo)
        else: # otherwise, update the name
            frame.teamInfo.updateData(teamName)

        if oldName != None:
            for file in os.listdir("SavedImages/Teams"):
                if file == oldName + ".png" and teamName != oldName:
                    file_ = "SavedImages/Teams/" + oldName + ".png"  
                    shutil.copy(file_, os.path.join("SavedImages/Teams", teamName + ".png"))

        if not imported: # after creating or editing a team, events need to be rebinded
            self.reBindEvents(parent, buttonFrame)
        else: # when importing, bind the events to the frame
            for widget in frame.winfo_children():
                if (isinstance(widget, ctk.CTkLabel) and widget.cget("text") == ""): # only bind the event to open the team menu to the logo
                    widget.bind("<Enter> <Button-1>", lambda event: self.openTeamMenu(event, frame))
            
                else: # bind another event (event to open the team) to the rest of the data
                    widget.bind("<Enter> <Button-1>", lambda event: self.editTeam(event, frame, teamName, stadiumName, teamLevel, logo, buttonFrame))
 
            # including the frame itself
            frame.bind("<Enter> <Button-1>", lambda event: self.editTeam(event, frame, teamName, stadiumName, teamLevel, logo, buttonFrame)) # and bind to the frame

        self.update_idletasks() # update the frame so that the new data is displayed

        if buttonFrame != None: # re-enable the create team button
            for button in buttonFrame.winfo_children():
                button.configure(state = "normal")
        
        self.logoImage = None # reset the logo image
        self.file = None # and the file
        self.searchButton.configure(state = "normal") # set the search button to normal
        src = Image.open("Images/search.png")
        self.searchButton.configure(image = ctk.CTkImage(src, None, (17, 17))) # and change its image to show its active

        if not imported: # after creating or editing, the team needs to be saved into the json files
            self.saveTeam(teamName, stadiumName, teamLevel, oldName, first, createPlayersVar) # save the team to the players.json file

    def create10Teams(self, parent, buttonFrame):
        numTeams = len(os.listdir("SavedImages/Teams")) # get the number of teams so that the first team is called "Team" + numTeams

        for i in range(10):
            # create the frame and all the necessary data
            createFrame = ctk.CTkFrame(parent, fg_color = ORANGE_BG, width = 350, height = 75)
            createFrame.pack(pady = 5)
            booleanVar = ctk.BooleanVar(value = False)
            nameVar = ctk.StringVar(value = "Team " + str(numTeams + i + 1))
            stadiumVar = ctk.StringVar(value = "Stadium Name")
            levelVar = ctk.IntVar(value = 100)

            # create the team
            self.createTeam(parent, createFrame, buttonFrame, nameVar, stadiumVar, levelVar, None, None, True, booleanVar)

    def reBindEvents(self, parent, buttonFrame):
        for frame in parent.teamsFrame.winfo_children(): # loop through each frame in the teamsFrame
            if len(frame.winfo_children()) == 4:
                # get the necessary data
                name = frame.teamInfo.name
                stadium = frame.winfo_children()[2].cget("text")
                level = frame.winfo_children()[3].cget("text")
                logoImg = frame.winfo_children()[0].cget("image")
                
                # and bind the events
                for widget in frame.winfo_children():
                    if(isinstance(widget, ctk.CTkLabel) and widget.cget("text") == ""): # only bind the event to logo
                        widget.bind("<Enter> <Button-1>", lambda event, f = frame: self.openTeamMenu(event, f))

                    else: # bind another event (event to open the team) to the rest of the data
                        widget.bind("<Enter> <Button-1>", lambda event, f = frame, tN = name, sN = stadium, tL = level, l = logoImg: self.editTeam(event, f, tN, sN, tL, l, buttonFrame))

                frame.bind("<Enter> <Button-1>", lambda event, f = frame, tN = name, sN = stadium, tL = level, l = logoImg: self.editTeam(event, f, tN, sN, tL, l, buttonFrame)) # and bind to the frame

    def destroyFrame(self, frame, parent, buttonFrame, teamName):
        # this function is only called when the user presses the "Delete" button when creating a team
        try:
            with open('teams.json', 'r') as file:
                teamsData = json.load(file)

            with open('players.json', 'r') as file:
                teams = json.load(file)
        except:
            teamsData = []
            teams = []
        
        # can only remove a team if its competition entry in teams.json
        remove = False
        teamSaved = True
        for i in range(len(teamsData)):
            if (teamsData[i]["name"] == teamName):
                teamSaved = True
                if (teamsData[i]["competitions"] == []):
                    remove = True
                    index = i
                break
            else:
                teamSaved = False

        if remove or not teamSaved:
            # use CTkMessagebox to ask the user if they are sure they want to delete the team
            question = CTkMessagebox(title = "Delete team", message = "Are you sure you want to delete this team?", icon = "question", option_1 = "Cancel", option_2 = "Yes", button_color = ORANGE_BG, fg_color = DARK_GRAY, cancel_button_color = DARK_GRAY, justify = "center")
            response = question.get()

            if response == "Cancel": # if no, exit
                return

            # remove the team's logo and remove the team from the teams.json file
            if teamName != None:
                os.remove("SavedImages/Teams/" + teamName + ".png")
                teamsData.pop(index)
                teams.pop(index)

                for file in os.listdir("SavedImages/Players"):
                    if (file.startswith(teamName + "_")):
                        os.remove("SavedImages/Players/" + file)

            with open('teams.json', 'w') as file:
                json.dump(teamsData, file)

            with open('players.json', 'w') as file:
                json.dump(teams, file)
            
            if(buttonFrame != None): # re-enable the create team button
                for button in buttonFrame.winfo_children():
                    button.configure(state = "normal")

            self.searchButton.configure(state = "normal")
            src = Image.open("Images/search.png")
            self.searchButton.configure(image = ctk.CTkImage(src, None, (17, 17)))

            frame.destroy() # destroy the frame
            self.reBindEvents(parent, buttonFrame)
            self.logoImage = None
        
        else:
            # use CTkMessagebox to inform the user that the team cannot be deleted
            CTkMessagebox(title = "Info", message = "Unable to delete team, it is part of a competition", icon = "info", fg_color = DARK_GRAY, justify = "center")

    def chooseLogo(self, parent, logoFrame, player = False):
        self.file = filedialog.askopenfilename(initialdir = "Images", title = "Select a logo", filetypes = (("png files", "*.png"), ("all files", "*.*"))) # get the file using a file dialog

        if(self.file): # get rid of errors if the user doesnt select an image
            src = Image.open(self.file)

            if not player:
                self.logoImage = ctk.CTkImage(src, None, (50, 50))
                logo = ctk.CTkLabel(logoFrame, image = self.logoImage, text = "")
                buttonX = 70
                buttonY = 65
            else:
                self.playerImage = ctk.CTkImage(src, None, (50, 50))
                logo = ctk.CTkLabel(logoFrame, image = self.playerImage, text = "")
                buttonX = 75
                buttonY = 65

            logo.pack(expand = True, fill = "both")

            # this button will allow the user to delete the logo if they want to and choose another one
            Xbutton = ctk.CTkButton(parent, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logo, Xbutton))
            Xbutton.place(x = buttonX, y = buttonY, anchor = "nw")

    def deleteLogo(self, logo, Xbutton):
        # this function will delete the logo and allow the user to choose another
        logo.pack_forget()
        Xbutton.place_forget()

        self.logoImage = None

    def createLogo(self, parent, logoFrame):

        def changeImage(direction):
            nonlocal activeLogo

            # this function will change the image to the next or previous logo and update activeLogo

            activeLogo += direction
            if activeLogo < 0:
                activeLogo = len(logos) - 1
            elif activeLogo >= len(logos):
                activeLogo = 0

            logoImage = ctk.CTkImage(Image.open(logos[activeLogo]), None, (100, 100))
            logo.configure(image = logoImage)

        def editLogo(logoPath):

            # once a logo is selected, create a new frame (on top of the logo selection frame) to edit the logo
            editLogoFrame = ctk.CTkFrame(self.parent.rootWindow, fg_color = ORANGE_BG, width = 350, height = 400)
            editLogoFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

            src = Image.open(logoPath) # using activeLogo (given in logoPath), get the correct logo
            logoImage = ctk.CTkImage(src, None, (160, 160))
            logo = ctk.CTkLabel(editLogoFrame, image = logoImage, text = "")
            logo.place(x = 15, y = 15, anchor = "nw")

            colorGroups, groupToColor = getColorGroups(logos[activeLogo]) # get the data
            src.save("Images/SampleLogos/modifiedLogoProgress.png") # save the image to a temp file

            if len(groupToColor) == 3: # set the locations and dimensions of eacg button depending on how many different colours there are in the logo (only 3 or 4 in the logos i use)
                button1x, button1y = 210, 25
                button2x, button2y = 210, 80
                button3x, button3y = 210, 135
                buttonW, buttonH = 125, 45
            else:
                button1x, button1y = 200, 25
                button2x, button2y = 200, 105
                button3x, button3y = 275, 25
                button4x, button4y = 275, 105
                buttonW, buttonH = 60, 65

            # create the buttons (3 buttons will have each button on top of another (expect the last ofc), 4 will have them in a square format)
            button1 = ctk.CTkButton(editLogoFrame, text = "", font = (APP_FONT, 15), fg_color = rgbToHex(groupToColor[0]), hover_color = rgbToHex(groupToColor[0]), width = buttonW, height = buttonH, corner_radius = 5, border_color = "red", border_width = 3)
            button1.configure(command = lambda: changeSelectedButton(button1))
            button1.place(x = button1x, y = button1y, anchor = "nw")
            buttons.append(button1)

            button2 = ctk.CTkButton(editLogoFrame, text = "", font = (APP_FONT, 15), fg_color = rgbToHex(groupToColor[1]), hover_color = rgbToHex(groupToColor[1]), width = buttonW, height = buttonH, corner_radius = 5)
            button2.configure(command = lambda: changeSelectedButton(button2))
            button2.place(x = button2x, y = button2y, anchor = "nw")
            buttons.append(button2)

            button3 = ctk.CTkButton(editLogoFrame, text = "", font = (APP_FONT, 15), fg_color = rgbToHex(groupToColor[2]), hover_color = rgbToHex(groupToColor[2]), width = buttonW, height = buttonH, corner_radius = 5)
            button3.configure(command = lambda: changeSelectedButton(button3))
            button3.place(x = button3x, y = button3y, anchor = "nw")
            buttons.append(button3)

            if len(groupToColor) == 4:
                button4 = ctk.CTkButton(editLogoFrame, text = "", font = (APP_FONT, 15), fg_color = rgbToHex(groupToColor[3]), hover_color = rgbToHex(groupToColor[3]), width = buttonW, height = buttonH, corner_radius = 5)
                button4.configure(command = lambda: changeSelectedButton(button4))
                button4.place(x = button4x, y = button4y, anchor = "nw")
                buttons.append(button4)

            # this frame will hold every colour button used to change the colour of the logo
            coloursFrame = ctk.CTkFrame(editLogoFrame, fg_color = GRAY, width = 340, height = 165, corner_radius = 0)
            coloursFrame.place(x = 5, y = 195, anchor = "nw")

            coloursFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11), weight = 1, uniform = "a")
            coloursFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight = 1, uniform = "a")
            coloursFrame.grid_propagate(False)

            # populate the frame with every button
            for i in range(len(RGBCOLORS)):
                row = i // 12
                col = i % 12

                colorButton = ctk.CTkButton(coloursFrame, text = "", font = (APP_FONT, 15), fg_color = rgbToHex(RGBCOLORS[i]), hover_color = rgbToHex(RGBCOLORS[i]), width = 10, height = 10, corner_radius = 0, command = lambda rgb = RGBCOLORS[i]: changeColorButton(rgb, logo, colorGroups, groupToColor))
                colorButton.grid(row = row, column = col, pady = 2)

            doneButton = ctk.CTkButton(editLogoFrame, text = "Done", font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 167, corner_radius = 5, command = lambda: finishLogo(editLogoFrame, logoFrame))
            doneButton.place(x = 5, y = 365, anchor = "nw")

            backButton = ctk.CTkButton(editLogoFrame, text = "Back", font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, width = 167, command = lambda: undoEditLogo(editLogoFrame))
            backButton.place(x = 177, y = 365, anchor = "nw")

        def undoEditLogo(frame):
            # this function will just go back to the logo selection frame while destroying the temp file and resetting the variables needed
            frame.destroy()
            os.remove("Images/SampleLogos/modifiedLogoProgress.png")
            buttons.clear()
            self.selectedButton = 0

        def finishLogo(frame, logoFrame):
            self.file = "Images/SampleLogos/modifiedLogoProgress.png" # set the file and logoImage variables to the temp file 
            self.logoImage = ctk.CTkImage(Image.open(self.file), None, (50, 50))
            logoLabel = ctk.CTkLabel(logoFrame, image = self.logoImage, text = "") # add the label to the logoFrame
            logoLabel.pack(expand = True, fill = "both")

            Xbutton = ctk.CTkButton(parent, text = "X", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, width = 15, height = 15, corner_radius = 5, command = lambda: self.deleteLogo(logoLabel, Xbutton))
            Xbutton.place(x = 70, y = 65, anchor = "nw")

            # desttoy both frames and pack the main menu again
            frame.destroy()
            chooseLogoFrame.destroy()
            self.parent.pack(expand = True, fill = "both")

        def undoCreateLogo(frame):
            # this function will go back to the main menu
            frame.destroy()
            self.parent.pack(expand = True, fill = "both")

        def getColorGroups(imagePath):
            # open the image and get the pixels
            image = Image.open(imagePath)
            pixels = image.load()

            # set the necessary data
            colorGroups = defaultdict(set)
            colorToGroup = {}
            groupToColor = {}

            # loop through every pixel
            for y in range(image.height):
                for x in range(image.width):
                    currentColor = pixels[x, y][:3]
                    if currentColor not in colorToGroup: # if the colour isnt already stored
                        groupId = len(colorToGroup) # get the id by the amount of colours already stored (0, 1, 2, 3...)
                        colorToGroup[currentColor] = groupId # link the id to the color
                        groupToColor[groupId] = currentColor # and the colour to the id
                    groupId = colorToGroup[currentColor] # get the id
                    colorGroups[groupId].add((x, y)) # and add the pixel to the colour group

            return colorGroups, groupToColor

        def changeSelectedButton(button):
            # this function is called whenever a colour button is called and it will change the value of selectedButton as well as change the border of the button to red to show it has been selected
            if button == buttons[0]:
                self.selectedButton = 0
                buttons[0].configure(border_color = "red", border_width = 3)
                buttons[1].configure(border_width = 0)
                buttons[2].configure(border_width = 0)
                if len(buttons) == 4:
                    buttons[3].configure(border_width = 0)

            elif button == buttons[1]:
                self.selectedButton = 1
                buttons[1].configure(border_color = "red", border_width = 3)
                buttons[0].configure(border_width = 0)
                buttons[2].configure(border_width = 0)
                if len(buttons) == 4:
                    buttons[3].configure(border_width = 0)

            elif button == buttons[2]:
                self.selectedButton = 2
                buttons[2].configure(border_color = "red", border_width = 3)
                buttons[0].configure(border_width = 0)
                buttons[1].configure(border_width = 0)
                if len(buttons) == 4:
                    buttons[3].configure(border_width = 0)
            else:
                self.selectedButton = 3
                buttons[3].configure(border_color = "red", border_width = 3)
                buttons[0].configure(border_width = 0)
                buttons[1].configure(border_width = 0)
                buttons[2].configure(border_width = 0)

        def rgbToHex(rgb):
            # simple function to change a rgb colour code to hex as ctk widgets can only take hex values and the colours in settings.py are stored as rbg values
            r, g, b = rgb
            return f'#{r:02x}{g:02x}{b:02x}'

        def changeColorButton(rgb, logo, colorGroups, groupToColor):
            # this function is called whenever a colour button is clicked and it will change the colour of the selected button to the colour of the button clicked
            hex = rgbToHex(rgb)
            buttons[self.selectedButton].configure(fg_color = hex, hover_color = hex)

            colorMapping = {self.selectedButton: rgb} # creates a mapping between the selectedButton (also a group id) and the colour
            imagePath = "Images/SampleLogos/modifiedLogoProgress.png"
            changeImageColors(imagePath, colorMapping, colorGroups, groupToColor, logo) # call the function to change the colour in the image
            groupToColor[self.selectedButton] = rgb # change the colour of the group to the new colour

        def changeImageColors(imagePath, colorMapping, colorGroups, groupToColor, logo):
            try: # open the image from the temp file and get the pixels
                image = Image.open(imagePath)
                pixels = image.load()
            except Exception as e:
                print(f"Error loading image: {e}")
                return

            # loop through the colour groups
            for groupId, positions in colorGroups.items():
                originalColor = groupToColor[groupId] # get the colour of the group
                newColor = colorMapping.get(groupId, originalColor) # get the new colour
                for x, y in positions: # loop through the pixels in the group and change their colour
                    if len(pixels[x, y]) == 4:
                        pixels[x, y] = newColor + (pixels[x, y][3],)
                    else:
                        pixels[x, y] = newColor

            # save the new image, overwriting the old one
            image.save("Images/SampleLogos/modifiedLogoProgress.png")

            # and set the image in the menu to the new one
            src = Image.open(imagePath)
            logoImage = ctk.CTkImage(src, None, (160, 160))
            logo.configure(image = logoImage)

        logos = []
        for i in range(21): # set the logos list with all the sample logos
            logos.append("Images/SampleLogos/logo" + str(i + 1) + ".png")

        activeLogo = 0 # this variable will store the index of the logo that the user is currently on

        self.parent.pack_forget() # remove the main menu

        # on this frame, the user will choose the logo they want to use
        chooseLogoFrame = ctk.CTkFrame(self.parent.rootWindow, fg_color = ORANGE_BG, width = 350, height = 165)
        chooseLogoFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        backButton = ctk.CTkButton(chooseLogoFrame, text = "X", font = (APP_FONT_BOLD, 10), fg_color = GRAY, text_color = "black", hover_color = CLOSE_RED, corner_radius = 5, height = 15, width = 15, command = lambda: undoCreateLogo(chooseLogoFrame))
        backButton.place(x = 5, y = 5, anchor = "nw")

        chooseButton = ctk.CTkButton(chooseLogoFrame, text = "Choose", font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 340, corner_radius = 5, command = lambda: editLogo(logos[activeLogo])) # give activeLogo to the editLogo function
        chooseButton.place(relx = 0.5, rely = 0.9, anchor = "center")

        leftArrow = ctk.CTkButton(chooseLogoFrame, text = "<", font = (APP_FONT, 35), fg_color = ORANGE_BG, hover_color = ORANGE_BG, text_color = "white", width = 15, corner_radius = 5, command = lambda: changeImage(-1))
        leftArrow.place(x = 75, y = 45, anchor = "nw")

        rightArrow = ctk.CTkButton(chooseLogoFrame, text = ">", font = (APP_FONT, 35), fg_color = ORANGE_BG, hover_color = ORANGE_BG, text_color = "white", width = 15, corner_radius = 5, command = lambda: changeImage(1))
        rightArrow.place(x = 275, y = 45, anchor = "ne")

        logoImage = ctk.CTkImage(Image.open(logos[0]), None, (100, 100))
        logo = ctk.CTkLabel(chooseLogoFrame, image = logoImage, text = "")
        logo.place(relx = 0.5, rely = 0.4, anchor = "center")

        buttons = [] # this list will hold the buttons to change colours so that they can be modified
        self.selectedButton = 0 # this variable will hold the index of whatever button is currently selected so that the correct colour can be modified

    def editTeam(self, event, frame, name, stadium, level, logo, buttonFrame):
        for widget in frame.winfo_children(): # destroy all the widgets in the frame
            widget.destroy() 

        # if a new season has begun, get the team's level from the players.json file (as it might have changed)
        if self.newSeason:
            try:
                with open("teamsBasic.json", "r") as file:
                    teams = json.load(file)
            except:
                teams = []

            for team in teams:
                if team["name"] == name:
                    level = team["level"]

        # recall the create menu function to allow the user to edit any team details
        self.createTeamMenu(self, buttonFrame, name, stadium, level, logo, frame, name, False)

    def saveTeam(self, name, stadium, level, oldName, first, manualPlayers):
        try:
            with open('players.json', 'r') as file:
                teams = json.load(file)

            with open('leaguesData.json', 'r') as file:
                leaguesData = json.load(file)
            
            with open('teams.json', 'r') as file:
                teamsData = json.load(file)

            with open("leagues.json", "r") as file:
                data = json.load(file)
        except:
            teams = []
            leaguesData = []
            teamsData = []
            data = []

        # find the team in the players.json file, this only used after editing a team, hence the oldName variable
        for i in range(len(teams)):
            if (teams[i]["name"] == oldName):
                teamIndex = i

        # create a new team entry for the players.json file
        team = {
            "name": name,
            "logoPath": "SavedImages/Teams/" + name + ".png",
            "players": [] if oldName == None else teams[teamIndex]["players"]
        }
        
        # create a new entry for the teams.json file
        teamBasic = {
            "name": name,
            "level": level,
            "stadium": stadium,
            "logoPath": "SavedImages/Teams/" + name + ".png",
            "competitions": [] if oldName == None else teamsData[teamIndex]["competitions"],
        }

        # if the user doesnt want to create their players manually, create 24 random players
        if manualPlayers.get() == False:
            fake = Faker()
            if first:
                for i in range(24):
                    name = fake.name_male()
                    name.replace("Mr. ", "").replace("Dr. ", "").replace(" PhD", "").replace(" MD", "").replace(" DVM", "").replace(".", "").replace(" DDS", "")

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

                    team["players"].append(player)

        # check if there is a team with the same name
        duplicate = False
        for i in range(len(teams)):
            if (teams[i]["name"] == name):
                duplicate = True
                break

        if not duplicate:
            teams.append(team)
            teamsData.append(teamBasic)
        else: # if there is a duplicate, replace the old team with the new one
            for i in range(len(teams)):
                if (teams[i]["name"] == oldName):
                    teams[i] = team
                    teamsData[i] = teamBasic
                    break
        
        # remove the team with the old name from the players.json file and remove its logo from the folder
        if oldName != None and oldName != name:
            for i in range(len(teams)):
                if teams[i]["name"] == oldName:
                    os.remove("SavedImages/Teams/" + oldName + ".png")
                    teams.pop(i)
                    teamsData.pop(i)
                    break
        
        # change the team's name and logo path in the leaguesData.json file for any competitons its in
        # for comp in teamBasic["competitions"]:
        #     for league in leaguesData:
        #         if comp == league["name"]:

        #             for leagueData in data: # find the number of divisions in the league
        #                 if comp == leagueData["name"]:
        #                     leagueDivs = leagueData["divisions"]

        #             if leagueDivs == 1:
        #                 for team in league["teams"]:
        #                     if (team["name"] == oldName):
        #                         team["name"] = name
        #                         team["logoPath"] = "SavedImages/Teams/" + name + ".png"
        #                         break
        #                 for matchDay in league["matchDays"]:
        #                     for match in matchDay["matches"]:
        #                         if (match["home"] == oldName):
        #                             match["home"] = name
        #                         if (match["away"] == oldName):
        #                             match["away"] = name
                    
        #             else:
        #                 for div in league["divisions"]:
        #                     for team in div["teams"]:
        #                         if (team["name"] == oldName):
        #                             team["name"] = name
        #                             team["logoPath"] = "SavedImages/Teams/" + name + ".png"
        #                             break
        #                     for matchDay in div["matchDays"]:
        #                         for match in matchDay["matches"]:
        #                             if (match["home"] == oldName):
        #                                 match["home"] = name
        #                             if (match["away"] == oldName):
        #                                 match["away"] = name

        with open("teams.json", "w") as file:
            json.dump(teamsData, file)

        with open('leaguesData.json', 'w') as file:
            json.dump(leaguesData, file)

        with open('players.json', 'w') as file:
            json.dump(teams, file)

        # if the user does want to create their players manually, call the function
        if manualPlayers.get():
            self.createPlayersManual(name)

    def createPlayersManual(self, teamName):
        # this frame will hold all the buttons that the user clicks on to create a player
        createPlayersFrame = ctk.CTkScrollableFrame(self.parent, fg_color = DARK_GRAY, height = 660, width = 355)
        createPlayersFrame.place(x = 1, y = 5)
 
        # add the goalkeeper label and buttons
        ctk.CTkLabel(createPlayersFrame, text = "Goalkeepers", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
        self.addButtons(createPlayersFrame, 3, [0.9, 0.05, 0.05], teamName, "goalkeeper", [1, 2, 3]) # give in the frame, number of buttons, startingChances, name of team, position of player and the indexes of the players

        # add the defender label and buttons
        ctk.CTkLabel(createPlayersFrame, text = "Defenders", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
        self.addButtons(createPlayersFrame, 8, [0.7, 0.71, 0.72, 0.69, 0.3, 0.29, 0.28, 0.31], teamName, "defender", [4, 5, 6, 7, 8, 9, 10, 11])

        # add the midfielder label and buttons
        ctk.CTkLabel(createPlayersFrame, text = "Midfielders", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
        self.addButtons(createPlayersFrame, 6, [0.7, 0.71, 0.69, 0.3, 0.31, 0.29], teamName, "midfielder", [12, 13, 14, 15, 16, 17])

        # add the forward label and buttons
        ctk.CTkLabel(createPlayersFrame, text = "Forwards", font = (APP_FONT, 15), fg_color = DARK_GRAY, text_color = "black").pack(expand = True, fill = "both", pady = (0, 5))
        self.addButtons(createPlayersFrame, 7, [0.8, 0.7, 0.71, 0.3, 0.29, 0.1, 0.1], teamName, "forward", [18, 19, 20, 21, 22, 23, 24])

        # once finished, this button will be enabled and it will simply remove the frame
        self.doneButton = ctk.CTkButton(createPlayersFrame, text = "Done", font = (APP_FONT, 15), fg_color = ORANGE_BG, text_color = "black", state = "disabled", corner_radius = 5, height = 30, width = 345, command = lambda: createPlayersFrame.place_forget())
        self.doneButton.pack(expand = True, fill = "both", pady = 5)

        try:
            with open("players.json", "r") as file:
                self.teamsManual = json.load(file)
        except:
            self.teamsManual = []

        self.counter = 0 # set a counter to 0

    def addButtons(self, frame, num, startingChances, teamName, pos, indexes):
        # this function will simply add however many buttons are needed to the frame and give the data to the addPlayerManual function
        for i in range (num):
            button = ctk.CTkButton(frame, text = "Add player", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 0, height = 28)
            button.configure(command = lambda chance = startingChances[i], b = button, index = indexes[i]: self.addPlayerManual(chance, b, teamName, pos, index))
            button.pack(expand = True, fill = "both", pady = (0, 5))

    def addPlayerManual(self, startingChance, button, teamName, position, playerIndex):
        button.configure(state = "disabled") # disable the button once it has been clicked

        # this frame will contain all of the data necessary to create the player
        playerFrame = ctk.CTkFrame(self.parent, fg_color = GRAY, height = 675, width = 380)
        playerFrame.place(x = 1, y = 5)

        logoFrame = ctk.CTkFrame(playerFrame, fg_color = GRAY, border_color = DARK_GRAY, border_width = 3, width = 75, height = 75)
        logoFrame.place(x = 15, y = 15, anchor = "nw")

        src = Image.open("Images/upload.png")
        uploadImage = ctk.CTkImage(src, None, (25, 25))

        logoButton = ctk.CTkButton(logoFrame, text = "", image = uploadImage, font = (APP_FONT_BOLD, 7), fg_color = DARK_GRAY, text_color = "black", width = 25, corner_radius = 5, command = lambda: self.chooseLogo(playerFrame, logoFrame, True))
        logoButton.place(relx = 0.5, rely = 0.5, anchor = "center")
        logoFrame.pack_propagate(False)

        nameEntry = ctk.CTkEntry(playerFrame, font = (APP_FONT, 15), fg_color = GRAY, text_color = "black", width = 200, border_color = DARK_GRAY)
        nameEntry.place(x = 110, y = 25, anchor = "nw")

        src = Image.open("SavedImages/Teams/" + teamName + ".png")
        team = ctk.CTkImage(src, None, (30, 30))
        ctk.CTkLabel(playerFrame, text = "", image = team).place(x = 110, y = 60, anchor = "nw")
        ctk.CTkLabel(playerFrame, text = teamName, font = (APP_FONT, 15), text_color = "black", fg_color = GRAY).place(x = 147, y = 61, anchor = "nw")

        ageFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 370, height = 50)
        ageFrame.place(x = 5, y = 120, anchor = "nw")
        ageNum = ctk.IntVar(value = 18)
        ctk.CTkLabel(ageFrame, text = "Age:", font = (APP_FONT, 20), text_color = "white").place(x = 10, y = 10, anchor = "nw")
        ageLabel = ctk.CTkLabel(ageFrame, text = "22", font = (APP_FONT, 20), text_color = "white")
        ageLabel.place(x = 330, y = 10, anchor = "nw")
        ageSlider = ctk.CTkSlider(ageFrame, from_ = 16, to = 45, width = 205, height = 23, fg_color = GRAY, button_color = "white", button_hover_color = "white", variable = ageNum, command = lambda value: self.printLabel(ageNum, ageLabel))
        ageSlider.set(22)
        ageSlider.place(x = 105, y = 15, anchor = "nw")

        numberFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 370, height = 50)
        numberFrame.place(x = 5, y = 175, anchor = "nw")
        numberNum = ctk.IntVar(value = 0)
        ctk.CTkLabel(numberFrame, text = "Number:", font = (APP_FONT, 20), text_color = "white", width = 10).place(x = 10, y = 10, anchor = "nw")
        numberLabel = ctk.CTkLabel(numberFrame, text = "0", font = (APP_FONT, 20), text_color = "white")
        numberLabel.place(x = 330, y = 10, anchor = "nw")
        numberSlider = ctk.CTkSlider(numberFrame, from_ = 0, to = 99, width = 205, height = 23, fg_color = GRAY, button_color = "white", button_hover_color = "white", variable = numberNum, command = lambda value: self.printLabel(numberNum, numberLabel))
        numberSlider.place(x = 105, y = 15, anchor = "nw")

        # this frame will contain buttons with images of different countries for the player's nationality
        nationalityFrame = ctk.CTkFrame(playerFrame, fg_color = DARK_GRAY, width = 370, height = 400)
        nationalityFrame.place(x = 5, y = 230, anchor = "nw")   
        nationalityFrame.grid_rowconfigure(0, weight = 2, uniform = "a")
        nationalityFrame.grid_rowconfigure((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12), weight = 1, uniform = "a")
        nationalityFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight = 1, uniform = "a")
        nationalityFrame.grid_propagate(False)

        ctk.CTkLabel(nationalityFrame, text = "Nationality", font = (APP_FONT, 20), text_color = "white").grid(row = 0, column = 0, columnspan = 3, sticky = "w", padx = 10)
        self.nationalityVar = ctk.StringVar(value = "united kingdom") # set the far to the default
        src = Image.open("Images/Countries/united kingdom.png") # load the image
        img = ctk.CTkImage(src, None, (30, 30))
        self.natImage = ctk.CTkLabel(nationalityFrame, text = "", image = img) # set natImage to the loaded image
        self.natImage.grid(row = 0, column = 5)

        countries = os.listdir("Images/Countries")

        # create each button for each country
        for i, country in enumerate(countries):
            src = Image.open("Images/Countries/" + country)
            img = ctk.CTkImage(src, None, (30, 30))

            row = i // 6 + 1
            column = i % 6

            buttonNat = ctk.CTkButton(nationalityFrame, text = "", image = img, hover_color = DARK_GRAY, fg_color = DARK_GRAY, width = 20, command = lambda country = country: self.changeCountry(country))
            buttonNat.grid(row = row, column = column)
        
        doneButton = ctk.CTkButton(playerFrame, text = "Done", font = (APP_FONT, 15), fg_color = ORANGE_BG, text_color = "black", corner_radius = 5, height = 30, width = 370, command = lambda: self.finishManual(playerFrame, nameEntry, ageNum, numberNum, startingChance, position, teamName, playerIndex, button))
        doneButton.place(x = 5, y = 635, anchor = "nw")

    def changeEntryText(self, var, entry):
        # This function simply changes the text of an entry when the variable changes (e.g. for the level slider, this function changes the text whenever the slider is moved)
        entry.delete(0, "end")
        entry.insert(0, str(var.get()))

    def printLabel(self, var, label):
        # This function simply changes the text of a label when the variable changes (e.g. for the age slider, this function changes the text whenever the slider is moved)
        label.configure(text = str(var.get()))

    def changeCountry(self, countryFile):
        # this function will change the image of the selected country as well as the nationalityVar whenever a country button is clicked
        src = Image.open("Images/Countries/" + countryFile)
        img = ctk.CTkImage(src, None, (30, 30))
        self.natImage.configure(image = img)
        self.nationalityVar.set(os.path.splitext(countryFile)[0])

    def finishManual(self, frame, nameEntry, ageNum, numberNum, chance, pos, teamName, playerIndex, button):
        # check that the name is correct (not empty or not too long)
        name = nameEntry.get()
        if name == "" or len(name) > 25:
            nameEntry.configure(border_color = "red")
            return # otherwise return and end the function

        self.counter += 1 # increase the counter by 1
        frame.place_forget() # remove the frame to allow the user to click on another button and create another player

        # add player data to the team's players list
        age = ageNum.get()
        number = numberNum.get()
        nationality = self.nationalityVar.get()

        # create a new entry for the player with all its data
        newEntry = {
            "name": name,
            "age": age,
            "number": number,
            "nationality": nationality.capitalize(),
            "position": pos,
            "startingChance": chance,
            "seasonStats": [],
            "matchBan": [],
            "matches": [],
            "seasonsData": [],
            "trophies": {}
        }

        for team in self.teamsManual:
            if team["name"] == teamName:
                team["players"].append(newEntry) # append the entry to the teams' players data

        # if an image for the player's face was used, then save it to the folder with the team name and index so that it can be found easily
        if self.playerImage != None:
            try:
                shutil.copy(self.file, os.path.join("SavedImages/Players", teamName + "_" + str(playerIndex )+ ".png"))
            except:
                pass
        
        self.playerImage = None # reset the player image

        button.configure(text = name) # change the text on the button from "Add player" to the player's name

        if self.counter == 24: # if every player was created, save the file and enable the done button
            with open("players.json", "w") as file:
                json.dump(self.teamsManual, file)

            self.doneButton.configure(state = "normal")

    def openTeamMenu(self, event, frame):
        self.parent.pack_forget() # remove the mainMenu so that the leagueMenu can be displayed

        # create a team menu for the team
        frame.teamInfo.place(x = 200, y = 350, anchor = "center")

        frame.teamInfo.teamFrame.addData()
        frame.teamInfo.recordsFrame.addRecords()
        frame.teamInfo.playersFrame.addPlayers()
            
    def getFontSize(self, name):
        if (len(name) > 10):
            self.fontsize = 20
        if (len(name) >= 15):
            self.fontsize = 15
        if (len(name) > 20):
            self.fontsize = 10
        if (len(name) > 25):
            self.fontsize = 5

    def updateLevels(self):
        # this function is called when a new season has begun, so that the team's levels can be updated
        self.newSeason = True

        try:
            with open('teams.json', 'r') as file:
                teams = json.load(file)
        except:
            teams = []

        # for each team, update the level label to the team's level
        for team in teams:
            for label in self.levelLabels:
                if (label[0] == team["name"]):
                    label[1].configure(text = team["level"])

    def searchTeams(self, string):
        if string == "":
            return # dont do anything is the string is empty

        self.resetButton.configure(state = "normal") # set the reset button to active and change its image to show that
        src = Image.open("Images/reset.png")
        self.resetButton.configure(image = ctk.CTkImage(src, None, (17, 17)))
        
        teamsAdd = [] # list that will contain the teams that match the search string

        try:
            with open('teams.json', 'r') as file:
                teams = json.load(file)
        except:
            teams = []
        
        for team in teams: # find the teams that match the search string
            if string.lower() in team["name"].lower():
                teamsAdd.append(team)
        
        self.deleteTeamFrames() # delete all the team frames currently displayed
        self.teamsFrame._parent_canvas.yview_moveto(0) # move the frame's scrollbar to the top

        if teamsAdd != []: # if there are teams to add, add them using the importData function
            self.importData(None, None, teamsAdd)

    def reset(self):
        self.searchEntry.delete(0, "end") # delete the string in the search entry

        self.resetButton.configure(state = "disabled") # disable the reset button and change its image
        src = Image.open("Images/resetDisabled.png")
        self.resetButton.configure(image = ctk.CTkImage(src, None, (17, 17)))

        self.deleteTeamFrames() # delete all the teams displayed
        self.importData(None, None) # import all the teams

    def deleteTeamFrames(self):
        # simple function that deletes all the team frames in the teamsFrame
        for widget in self.teamsFrame.winfo_children():
            widget.destroy()

# Class that oversees the settings of the app    
class SettingsMenu(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(expand = True, fill = "both")

        settingsFrame = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 350, height = 200)
        settingsFrame.pack(expand = True, fill = "both")

        # buttons for auto sim speed
        ctk.CTkLabel(settingsFrame, text = "Auto Sim speed", font = (APP_FONT_BOLD, 15), text_color = "black").place(x = 10, y = 20, anchor = "nw")
        buttonVF = ctk.CTkButton(settingsFrame, text = "Very Fast", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, width = 15, command = lambda: self.changeAutoSpeed(0))
        buttonVF.place(x = 145, y = 20, anchor = "nw")
        buttonF = ctk.CTkButton(settingsFrame, text = "Fast", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", width = 50,  corner_radius = 5, command = lambda: self.changeAutoSpeed(1))
        buttonF.place(x = 200, y = 20, anchor = "nw")
        buttonS = ctk.CTkButton(settingsFrame, text = "Slow", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", width = 50, corner_radius = 5, command = lambda: self.changeAutoSpeed(2))
        buttonS.place(x = 253, y = 20, anchor = "nw")
        buttonVS = ctk.CTkButton(settingsFrame, text = "Very Slow", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, width = 15, command = lambda: self.changeAutoSpeed(3))
        buttonVS.place(x = 306, y = 20, anchor = "nw")

        # buttons for level changes
        ctk.CTkLabel(settingsFrame, text = "Level changes", font = (APP_FONT_BOLD, 15), text_color = "black").place(x = 10, y = 60, anchor = "nw")
        lButtonOn = ctk.CTkButton(settingsFrame, text = "On", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, width = 50, command = lambda: self.changeLevels(1))
        lButtonOn.place(x = 145, y = 60, anchor = "nw")
        lButtonOff = ctk.CTkButton(settingsFrame, text = "Off", font = (APP_FONT, 10), fg_color = GRAY, text_color = "black", corner_radius = 5, width = 50, command = lambda: self.changeLevels(0))
        lButtonOff.place(x = 200, y = 60, anchor = "nw")

        # list for auto sim speed and speeds
        self.buttonsSpeed = [buttonVF, buttonF, buttonS, buttonVS]
        self.autoSpeeds = [0, 1, 2, 3]

        # list for level changes and values
        self.levelButtons = [lButtonOff, lButtonOn]
        self.levelValues = [0, 1]

        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
        except:
            settings = []

        # set the active speed to the index in the settings
        self.activeSpeed = self.buttonsSpeed[settings["autoSpeed"]]
        self.activeSpeed.configure(fg_color = DARK_GRAY)

        # set the active level to the index in the settings
        self.activeLevel = self.levelButtons[settings["levelChange"]]
        self.activeLevel.configure(fg_color = DARK_GRAY)
    
    def changeAutoSpeed(self, speed):
        if speed == self.buttonsSpeed.index(self.activeSpeed):
            return # if the active button is pressed, do nothing
    
        # when clicking on a button, change the colour of button pressed to dark gray and the one before to gray
        self.activeSpeed.configure(fg_color = GRAY)
        self.activeSpeed = self.buttonsSpeed[speed]
        self.activeSpeed.configure(fg_color = DARK_GRAY)

        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
        except:
            settings = []

        settings["autoSpeed"] = speed # save the new speed

        with open("settings.json", "w") as file:
            json.dump(settings, file)

    def changeLevels(self, value):
        if value == self.levelButtons.index(self.activeLevel):
            return # if the active button is pressed, do nothing

        # when clicking on a button, change the colour of button pressed to dark gray and the one before to gray
        self.activeLevel.configure(fg_color = GRAY)
        self.activeLevel = self.levelButtons[value]
        self.activeLevel.configure(fg_color = DARK_GRAY)

        try:
            with open("settings.json", "r") as file:
                settings = json.load(file)
        except:
            settings = []

        settings["levelChange"] = value # save the new level change

        with open("settings.json", "w") as file:
            json.dump(settings, file)