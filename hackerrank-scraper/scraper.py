from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class Competitor:
    competitorList = []

    def __init__(self, position, username, completedCount):
        self.position = position
        self.username = username
        self.completedCount = completedCount

    def __str__(self):
        return '{0:<5} {1:<25} {2:<5}'.format(self.position, self.username, 
                self.completedCount)

    def __repr__(self):
        return self.__str__()

class Scraper:
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.loggedin = False

    def print_clean_usernames_from_page(self, leadersTableElement):
        userListBoxes = leadersTableElement.find_elements_by_class_name("leaderboard-list-view")
        competitorList = []
        for listbox in userListBoxes:
            row = listbox.find_element_by_class_name("row ")
            number = row.find_elements_by_css_selector(".span-flex-1.acm-leaderboard-cell")[0]
            nameCell = row.find_elements_by_css_selector(".span-flex-2.acm-leaderboard-cell")[0]
            completedCell = row.find_elements_by_css_selector(".span-flex-1.acm-leaderboard-cell")[1]
            competitorToAdd = Competitor(number.text, nameCell.text, completedCell.text)
            Competitor.competitorList.append(competitorToAdd)
            competitorList.append(competitorToAdd)

        return competitorList

        
    def load_leaderboard_pages(self, leaderboardURL):
        self.driver.implicitly_wait(30)
        pageSource = ""
        pageNumber = 1
        while not "Sorry, we require a few more submissions" in pageSource:
            #print("Loading leaderboard section {}".format(pageNumber))
            self.driver.get('{}/{}'.format(leaderboardURL, pageNumber))
            #print("Waiting for leaderboard JS to render...")
            pageSource = self.driver.page_source
            if "Sorry, we require a few more submissions" in pageSource:
                break
            WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.CLASS_NAME, "leaderboard-list-view"))
            )
            #print("JS Done.. processing elements")
            leaderboardElement = self.driver.find_element_by_id("leaders")
            pageSource = self.driver.page_source
            done = False
            while not done:
                try:
                    yield self.print_clean_usernames_from_page(leaderboardElement)
                    done = True
                except Exception:
                    continue
            pageNumber += 1



    def login(self, username, password):
        self.driver.get('https://www.hackerrank.com/login')
        WebDriverWait(self.driver, 100).until(
                EC.presence_of_element_located((By.NAME, "login"))
        )
        usernameField = self.driver.find_element_by_name('login')
        passwordField = self.driver.find_element_by_name('password')
        usernameField.send_keys(username)
        passwordField.send_keys(password)
        passwordField.send_keys(Keys.RETURN)
        WebDriverWait(self.driver, 100).until (
                EC.presence_of_element_located((By.CLASS_NAME, "feed-id"))
        )
        self.loggedin = True


    def scrape(self):
        configDict = {}
        with open('config.json', 'r') as openConfigFile:
            configDict = json.loads(openConfigFile.read())

        if not self.loggedin:
            self.login(configDict['username'], configDict['password'])
        for list in self.load_leaderboard_pages(configDict['leaderboard_url']):
            yield list
