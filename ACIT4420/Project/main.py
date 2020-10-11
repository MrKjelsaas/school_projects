"""
PROJECT DESCRIPTION

Project no. 1 - Website crawler
Create a python project that is able to download websites and capture sensitive data on the site

The program has to accept the following parameters:
- The start URL of the web crawling
- The depth of the crawling which means how many jumps has to be considered when downloading the website
- User defined regular expressions to find sensitive data

The program should provide the following features:
- Download the website from the provided URL, identify links inside the source code and download all website subpages that are linked until the maximum number of jumps are reached
- Identify email addresses and phone numbers and create a list of the captured values
- Identify comments inside the source code and make a list of them indicating the file name and line number of the comment
- Identify special data using the user provided regular expression
- Create a list of the most common words used on the crawled websites

"""

import requests
from bs4 import BeautifulSoup
import re
import string

def find_all_URLs(URL):
    try:
        found_URLs = []
        try:
            result = requests.get(URL, timeout=5)
        except:
            return []
        URL_soup = BeautifulSoup(result.content, 'html.parser')

        for URL in URL_soup.find_all('a'):
            link = URL.get('href')
            try:
                if link[:4] != "http":
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

# Set to True to output which URL is being searched
print_url_checking = False
print_scraping = False







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
        start_URL_result = requests.get(start_url, timeout=5)
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
URLs_to_crawl = [] # The URLs that we are going to scrape for info (email, phone number, etc.)
next_debth_URLs = [start_url] # The next URLs we are going to look for URLs in
debth_crawled = 0

print("Starting to look for URLs...\n")
while debth_crawled < crawl_debth + 1:


    found_URLs = [] # The list of URLs that are found during the current debth of the search

    for url in next_debth_URLs:
        if print_url_checking == True:
            print("Finding URLs in:", url)

        for found_url in find_all_URLs(url): # Finds URLs on a page and appends them if it's not already found
            if found_url not in found_URLs:
                if found_url not in next_debth_URLs:
                    if found_url not in URLs_to_crawl:
                        found_URLs.append(found_url)

    for url in next_debth_URLs:
        if url not in URLs_to_crawl:
            URLs_to_crawl.append(url)

    next_debth_URLs = found_URLs # These are the URLs we are going to scrape if we're going another level deeper

    debth_crawled += 1

print("\n\nDone looking for URLs\n")

print("Number of URLs found:")
print(len(found_URLs))
print("\n\n")





print("Starting to scrape the found URLs\n")
valid_symbols = string.ascii_lowercase + "æøå" + "'" + "-"  # We assume that all words only contain latin letters and dashes and apostrophes
list_of_words_found = []

for url in URLs_to_crawl:
    try:
        result = requests.get(url, timeout=5)
    except:
        pass
    URL_soup = BeautifulSoup(result.content, 'html.parser')

    if print_scraping == True:
        print("Now scraping:", url)

    URL_text = URL_soup.get_text().split()

    for word in URL_text:
        nameholder = ""
        for character in word:
            if character.lower() in valid_symbols:
                nameholder += character.lower()
            else:
                nameholder = ""
                break
        if len(nameholder) > 0:
            if len(list_of_words_found) > 0:
                for n in range(len(list_of_words_found)):
                    if nameholder == list_of_words_found[n][0]:
                        list_of_words_found[n][1] += 1
                        break
                    if n == len(list_of_words_found)-1:
                        list_of_words_found.append([nameholder, 1])
                        break
            elif len(list_of_words_found) == 0:
                list_of_words_found.append([nameholder, 1])

print("\nFinished finding words in URLs\n")

print("")
print("\nNumber of words found:", len(list_of_words_found))

words_with_more_than_one_occurence = 0
for word, amount in list_of_words_found:
    if amount > 1:
        words_with_more_than_one_occurence += 1
print("Words with more than one occurence:", words_with_more_than_one_occurence)



print("\nNumber of URLs scraped:", len(URLs_to_crawl), "\n")































# Placeholder
