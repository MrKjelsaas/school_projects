"""
PROJECT DESCRIPTION

Project no. 1 - Website crawler
Create a python project that is able to download websites and capture sensitive data on the site

The program has to accept the following parameters:
- The start URL of the web crawling
- The depth of the crawling which means how many jumps has to be considered when downloading the website
- User defined regular expressions to find sensitive data

The program should provide the following features:
- Download the website from the provided URL, identify links inside the source code and download all website subpages that are linked until the maximum number of jumps are not reached
- Identify email addresses and phone numbers and create a list of the captured values
- Identify comments inside the source code and make a list of them indicating the file name and line number of the comment
- Identify special data using the user provided regular expression
- Create a list of the most common words used on the crawled websites

"""

import requests
from bs4 import BeautifulSoup

def find_all_URLs(URL):
    try:
        found_URLs = []
        result = requests.get(URL)
        URL_soup = BeautifulSoup(result.content, 'html.parser')

        for URL in URL_soup.find_all('a'):
            link = URL.get('href')
            try:
                if link[0:4] != "http":
                    continue
                if link in found_URLs:
                    continue
                if link[-4:] == ".pdf":
                    continue
                if link[-4:] == ".jpg":
                    continue
                if link[-4:] == ".zip":
                    continue
                if link[-5:] == ".docx":
                    continue

                found_URLs.append(URL.get('href'))
            except:
                pass

        return found_URLs

    except:
        return []

print_url_checking = True







# Create a python project that is able to download websites and capture sensitive data on the site
print("\n-----\n\nWelcome to my web crawler")

# The program has to accept the following parameters:
# - The start URL of the web crawling
valid_url = False
while valid_url is False:
    start_url = str(input("\nPlease enter the start url (enter \"exit\" to quit): "))
    start_url = start_url.lower()
    if start_url == "exit":
        print("\nExiting program...\n")
        exit()
    # Control the URL
    # Check that it starts with http://www.
    if start_url[0:4] == "www.":
        start_url = "http://" + start_url
    if not((start_url[0:11] == "http://www.") or (start_url[0:12] == "https://www.")):
        start_url = "http://www." + start_url

    try:
        start_URL_result = requests.get(start_url)
        valid_url = True
    except:
        print("Invalid URL, please try again")

del valid_url

# - The depth of the crawling which means how many jumps has to be considered when downloading the website
valid_crawl_debth = False
while valid_crawl_debth == False:
    try:
        crawl_debth = int(input("Please enter the debth of the crawl: "))
        valid_crawl_debth = True
        if crawl_debth < 0:
            valid_crawl_debth = False
    except:
        print("Invalid debth, please try again\n(hint: must be an integer)")

del valid_crawl_debth
print("\nCrawling", start_url, "with a debth of", crawl_debth, "\n")

# - User defined regular expressions to find sensitive data
user_defined_regexes = []
inputting_defined_regexes_is_done = False
while inputting_defined_regexes_is_done == False:
    regex_input = str(input("Please enter a word to look for (leave blank to finish): "))
    if len(regex_input) > 0:
        user_defined_regexes.append(regex_input)
    if len(regex_input) == 0:
        inputting_defined_regexes_is_done = True

del inputting_defined_regexes_is_done





print("\nAnd thus commences the crawl\n\n")

# Make a list of URLs to visit
URL_list = []

debth_crawled = 0

next_debth_URLs = [start_url]

while debth_crawled < crawl_debth + 1:
    found_URLs = []
    for url in next_debth_URLs:
        if print_url_checking == True:
            print("Now checking:", url)

        for found_url in find_all_URLs(url):
            if found_url not in found_URLs:
                if found_url not in next_debth_URLs:
                    found_URLs.append(found_url)

    for url in next_debth_URLs:
        if url not in URL_list:
            URL_list.append(url)

    next_debth_URLs = found_URLs

    for url in next_debth_URLs:
        if url not in URL_list:
            URL_list.append(url)

    debth_crawled += 1




print("\n\nDone crawling\n")

print("\n\n")

print("Number of URLs found:")
print(len(URL_list))


































# Placeholder
