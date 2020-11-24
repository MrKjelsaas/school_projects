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
                if link[:5] != "https":
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

def find_all_phone_numbers(input):
    numbers_found = []

    # Looking for Norwegian phone numbers on the standard form
    results = re.findall("\d{8}", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+\d{10}", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("^\+\d\d \d\d \d\d \d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+ *\d\d \d\d \d\d \d\d \d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("^\+\d\d\d \d\d \d\d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+ *\d\d\d \d\d \d\d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    """
    # This finds North American numbers as well, but also a lot of crap
    results = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', input)
    for result in results:
        if result not in numbers_found:
            numbers_found.append(result)
    """

    return numbers_found

def find_all_emails(input):
    emails_found = []

    results = re.findall("\w+@\w+\.[a-zA-Z]{2,4}", input)
    for result in results:
        if result not in emails_found:
            emails_found.append(result)

    return emails_found



# Set to True to output which URL is being searched
print_url_checking = False
print_scraping = False










# Create a python project that is able to download websites and capture sensitive data on the site
print("\n----------\n\nWelcome to my web crawler")

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
        start_url = "https://" + start_url
    if not(start_url[0:12] == "https://www."):
        start_url = "https://www." + start_url

    try:
        start_URL_result = requests.get(start_url, timeout=5)
        valid_url = True
    except:
        print("Invalid URL, please try again")

del valid_url # Just to show that I know about memory management

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
        user_defined_regexes.append(regex_input.lower())
    if len(regex_input) == 0:
        inputting_defined_regexes_is_done = True

del inputting_defined_regexes_is_done













# Make a list of URLs to visit
URLs_to_crawl = [] # The URLs that we are going to scrape for info (email, phone number, etc.)
next_debth_URLs = [start_url] # The next URLs we are going to look for URLs in
debth_crawled = 0

print("\n\nStarting to look for URLs...\n")
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

print("\nDone looking for URLs\n")

total_URLs_found = len(URLs_to_crawl)
for n in range(len(next_debth_URLs)):
    if next_debth_URLs[n] not in URLs_to_crawl:
        total_URLs_found += 1
print("Number of URLs found:", total_URLs_found)
print("\n")









print("Starting to scrape the found URLs\n")
valid_symbols = string.ascii_lowercase + "æøå-'" # We assume that valid words only contain latin letters and dashes and apostrophes
list_of_words_found = []
list_of_phone_numbers_found = []
list_of_emails_found = []

for url in URLs_to_crawl:
    try:
        result = requests.get(url, timeout=5)
    except:
        continue
    URL_soup = BeautifulSoup(result.content, 'html.parser')

    if print_scraping == True:
        print("Now scraping:", url)

    # Extracts the text from a website
    URL_text = " ".join(URL_soup.strings)



    # Looks for phone numbers
    for number in find_all_phone_numbers(URL_text):
        if number not in list_of_phone_numbers_found:
            list_of_phone_numbers_found.append(number)

    # Looks for emails
    for email in find_all_emails(URL_text):
        if email not in list_of_emails_found:
            list_of_emails_found.append(email)

    # Looks for valid words
    URL_text = URL_text.split()

    for word in URL_text:
        nameholder = ""
        for character in word:
            if character.lower() in valid_symbols:
                nameholder += character.lower()
            else: # If word contains invalid character, skip it
                nameholder = ""
                break
        if len(nameholder) > 0: # If it found a word
            if len(list_of_words_found) > 0: # Check if it is already found
                for n in range(len(list_of_words_found)):
                    if nameholder == list_of_words_found[n][0]:
                        list_of_words_found[n][1] += 1
                        break
                    elif n == len(list_of_words_found)-1:
                        list_of_words_found.append([nameholder, 1])
            elif len(list_of_words_found) == 0:
                list_of_words_found.append([nameholder, 1])







print("\nFinished scraping the URLs\n")

print("\nNumber of words found:", len(list_of_words_found))

words_with_more_than_one_occurence = 0
for word, amount in list_of_words_found:
    if amount > 1:
        words_with_more_than_one_occurence += 1
print("Words with more than one occurence:", words_with_more_than_one_occurence)

print("\nNumber of URLs scraped:", len(URLs_to_crawl), "\n")



print("\nLooking for user defined regexes\n")
occurence_of_user_regexes = []
for regex in user_defined_regexes:
    occurence_of_user_regexes.append([regex, 0])

for i in range(len(user_defined_regexes)):
    for j in range(len(list_of_words_found)):
        if list_of_words_found[j][0] == user_defined_regexes[i]:
            occurence_of_user_regexes[i][1] = list_of_words_found[j][1]
            break

for user_regex, occurence in occurence_of_user_regexes:
    print(user_regex, "occured", occurence, "times")


# Shows all emails found
if len(list_of_emails_found) == 0:
    print("\nDidn't find any emails")
else:
    print("\nNumber of emails found:", len(list_of_emails_found))

    print("Emails found:")
    for email in list_of_emails_found:
        print(email)


# Shows all phone numbers found
if len(list_of_phone_numbers_found) == 0:
    print("\nDidn't find any phone numbers")
else:
    print("\nNumber of phone numbers found:", len(list_of_phone_numbers_found))

    print("Phone numbers found:")
    for number in list_of_phone_numbers_found:
        print(number)






















# Placeholder
