import customtkinter as ctk
from ctypes import windll
from settings import *
from menu import *
import threading

class FootballSim(ctk.CTk):
    def __init__(self):
        super().__init__()

        # setup
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
        self.iconbitmap("Images/appIconAI.ico")
        self.title("League Master")
        ctk.set_appearance_mode("dark")
        self.geometry(str(APP_SIZE[0]) + "x" + str(APP_SIZE[1]))
        self.resizable(False, False)

        # orange loading screen with logo and progress bar
        self.loadingScreen = ctk.CTkFrame(self, fg_color = ORANGE_BG, width = 391, height = 691)
        self.loadingScreen.place(x = 5, y = 5)

        appLogo = ctk.CTkLabel(self.loadingScreen, text = "", image = ctk.CTkImage(Image.open("Images/appLogoAI.png"), None, (350, 350)))
        appLogo.place(relx = 0.5, rely = 0.25, anchor = "center")

        appTitle = ctk.CTkLabel(self.loadingScreen, text = "LEAGUE MASTER", text_color = "black", font = (APP_FONT_BOLD, 35))
        appTitle.place(relx = 0.5, rely = 0.55, anchor = "center")

        self.loadingLabel = ctk.CTkLabel(self.loadingScreen, text = "Starting app... 0%", text_color = "black", font = (APP_FONT, 20))
        self.loadingLabel.place(relx = 0.5, rely = 0.95, anchor = "center")

        self.loadingSlider = ctk.CTkSlider(self.loadingScreen, from_ = 0, to = 100, number_of_steps = 100, height = 20, width = 250, fg_color = GRAY, progress_color = DARK_GRAY, button_color = DARK_GRAY, corner_radius = 15, border_color = DARK_GRAY, border_width = 2, button_length = 0, state = "disabled")
        self.loadingSlider.place(relx = 0.5, rely = 0.91, anchor = "center")
        self.loadingSlider.set(0)
        
        # this threading will start loading the menu
        threading.Thread(target = self.loadMenu, args = (self.loadingScreen, self.loadingLabel, self.loadingSlider), daemon = True).start()

        self.mainloop()

    def loadMenu(self, screen, label, slider):
        self.mainMenu = MainMenu(self, screen, label, slider)

if __name__ == "__main__":
    FootballSim()