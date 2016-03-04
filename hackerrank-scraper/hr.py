from scraper import Scraper

scr = Scraper()
for competitorListChunk in scr.scrape():
    for competitor in competitorListChunk:
        print(competitor)
