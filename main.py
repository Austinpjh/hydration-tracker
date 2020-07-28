from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from database import DataBase


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
api = ServiceAccountCredentials.from_json_keyfile_name("api.json", scope)
client = gspread.authorize(api)
sheet = client.open("hydration_data").sheet1



class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        if self.namee.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0 and self.password != "":
            if self.email.text.strip() not in db.users:
                db.add_user(self.email.text, self.password.text, self.namee.text)
                NewRow = [self.namee.text, self.email.text, db.get_date(), db.update()]
                sheet.append_row(NewRow)
                self.reset()

                sm.current = "login"
            else:
                invalidEmail()
        else:
            invalidForm()

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.email.text, self.password.text):
            MainWindow.current = self.email.text
            self.reset()
            sm.current = "main"

        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    date = ObjectProperty(None)
    email = ObjectProperty(None)
    intake = ObjectProperty(None)
    input = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"
        self.input.text = ""

    def on_enter(self, *args):
        password, name, created, water = db.get_user(self.current)
        self.n.text = "Account Name: " + name
        self.email.text = "Email: " + self.current
        if db.get_date() != created:
            water = "0"
            self.intake.text = "Total Water Intake: " + water + " ml"
            self.date.text = "Date: " + db.get_date()
            db.users[self.current] = (password, name, db.get_date(), water)
            db.save()
            NewRow = [name, self.current, db.get_date(), water]
            sheet.append_row(NewRow)
        else:
            self.intake.text = "Total Water Intake: " + water + " ml"
            self.date.text = "Date: " + created

    def water_update(self):
        if self.input.text.isdecimal() == False :
            invalidInput()
        else:
            password, name, created, intake = db.get_user(self.current)
            intake = int(intake) + int(self.input.text)
            db.users[self.current] = (password, name, db.get_date(), str(intake).strip())
            db.save()
            self.intake.text = "Total Water Intake: " + str(intake) + " ml"
            list_of_cells = sheet.findall(self.current)
            sheet.update_cell(list_of_cells[-1].row, 4, str(intake))



class WindowManager(ScreenManager):
    pass


def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.', font_size=30),
                  size_hint=(0.5, 0.5))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.', font_size=25),
                  size_hint=(0.5, 0.5))

    pop.open()


def invalidEmail():
    pop = Popup(title='Invalid Form',
                  content=Label(text='This email has already been used before.', font_size=25),
                  size_hint=(0.5,0.5))

    pop.open()

def invalidInput():
    pop = Popup(title='Invalid Input',
                  content=Label(text='Please enter a valid volume of water.', font_size=25),
                  size_hint=(0.5,0.5))

    pop.open()

kv = Builder.load_file("water.kv")

sm = WindowManager(transition=FadeTransition())
db = DataBase("users.txt")

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"),MainWindow(name="main")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()
