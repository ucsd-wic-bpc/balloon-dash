hackerrank-scraper
==================
A tool made to get information from a currently running Hackerrank competition's
leaderboards.

Goals
--------
This tool's goals are two-fold:

1. Access the leaderboards of any programming competition, even if the 
   competition is private.

2. Provide the gained information in an easy to use API.



Methods
-------
In order to accomplish goals, the following steps must be taken:

1. Allow the user to provide the competition name and login credentials to
   access private competitions. Login and ensure that the login session is 
   saved. Render the leaderboard of the requested competition and retrieve the
   source code.

2. Parse the source code and insert the retrieved data into a meaningful Python
   datastructure.



Research
--------
The following research has been done to accomplish these tasks:

[We may want to use Python WebKit](https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/)  
[Here is another WebKit example](https://webscraping.com/blog/Scraping-JavaScript-webpages-with-webkit/)

Current Model
-------------
Although much research has been done regarding the use of WebKit, etc. Selenium
allowed for a unique and functional solution. The current package uses Selenium.


Installation/Use
----------------
Using hackerrank-scraper for the first time is easy:  
1. `pip install -r requirements.txt`  
2. Fill config.json  
3. python hr.py
