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



# Set to True to output info
print_url_checking = False
print_scraping = False
print_found_emails = False
print_found_phone_numbers = False
print_found_words = False
print_most_frequently_used_words = False
print_comments_found = False
print_user_defined_regexes = True
print_number_of_words_found = False
print_words_with_more_than_one_occurence = False



def find_all_URLs(URL):
    found_URLs = []
    try:
        result = requests.get(URL, timeout=5)
    except:
        return []
    URL_soup = BeautifulSoup(result.content, 'html.parser')

    for link in re.findall("href\=\"https[:\/.a-zA-Z0-9]+\"", URL_soup.prettify()):
        link = link[6:-1]
        try: # In the rare cases of getting a really weird link
            if link[:8] != "https://":
                continue
            if link[-4:] == ".pdf":
                continue
            if link[-4:] == ".jpg":
                continue
            if link[-4:] == ".zip":
                continue
            if link[-5:] == ".docx":
                continue
            found_URLs.append(link)
        except:
            pass

    return found_URLs


def find_all_phone_numbers(input):
    numbers_found = []

    # Looking for Norwegian phone numbers on the standard form
    results = re.findall("^\+\d{8}", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+\d{10}", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("^[+]\d\d \d\d \d\d \d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+\d\d \d\d \d\d \d\d \d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("^[+]\d\d\d \d\d \d\d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    results = re.findall("\+\d\d[ ]*\d\d\d \d\d \d\d\d", input)
    for result in results:
        result = result.replace(" ", "")
        if result not in numbers_found:
            numbers_found.append(result)

    for number in numbers_found:
        if number[:3] != "+47":
            number = "+47" + number

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

    results = re.findall("[\w\.\-\_]+@\w+\.[a-zA-Z]{2,4}", input)
    for result in results:
        if result not in emails_found:
            emails_found.append(result)

    return emails_found

def find_all_words(input):
    words_found = []
    for result in re.findall("[a-zA-ZæøåÆØÅ'\-]+", input):
        result = result.lower()

        if result == "-" or result == "--":
            continue
        if result[0] == "-":
            result = result[1:]
        if result[-1] == "-":
            result = result[:-1]

        if result not in words_found:
            words_found.append([result, 1])
        else:
            words_found.index(result)[1] += 1
    return words_found













# Create a python project that is able to download websites and capture sensitive data on the site
print("\n\n\n--------------------\n\n\nWelcome to my web crawler")

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









print("Starting to scrape", len(URLs_to_crawl), "URLs\n")

list_of_words_found = []
list_of_phone_numbers_found = []
list_of_emails_found = []
list_of_comments_found = []

for url in URLs_to_crawl:
    try:
        result = requests.get(url, timeout=5)
    except:
        continue

    # Extracts the text from a website
    URL_soup = BeautifulSoup(result.content, 'html.parser')

    if print_scraping == True:
        print("Now scraping:", url)

    # Looks for phone numbers
    for number in find_all_phone_numbers(URL_soup.get_text()):
        if number not in list_of_phone_numbers_found:
            list_of_phone_numbers_found.append(number)

    # Looks for emails
    for email in find_all_emails(URL_soup.get_text()):
        if email not in list_of_emails_found:
            list_of_emails_found.append(email)

    # Looks for valid words
    for word, amount in find_all_words(" ".join(URL_soup.stripped_strings)):
        word_found = False
        if len(list_of_words_found) == 0:
            list_of_words_found.append([word, amount])
        else:
            for n in range(len(list_of_words_found)):
                if list_of_words_found[n][0] == word:
                    word_found = True
                    list_of_words_found[n][1] += amount
                    break
            if word_found == False:
                list_of_words_found.append([word, amount])

    # Look for comments in the source code
    try: # Can get a recursion error when decoding websites
        result = URL_soup.prettify().split("\n")
        for n in range(len(result)):
            temp = re.findall("<!-- .* -->", result[n])
            if temp is not None:
            #if "<!--" in result[n]:
                for index in temp:
                    list_of_comments_found.append([index[5:-4], n, url])
    except:
        continue





print("\nFinished scraping the URLs\n")
print("\n-----\n\n")











if print_number_of_words_found == True:
    print("\nNumber of words found:", len(list_of_words_found))

words_with_more_than_one_occurence = 0
for word, amount in list_of_words_found:
    if amount > 1:
        words_with_more_than_one_occurence += 1

if print_words_with_more_than_one_occurence == True:
    print("Words with more than one occurence:", words_with_more_than_one_occurence)

print("\nNumber of URLs scraped:", len(URLs_to_crawl), "\n")





# Shows occurence of user defined regexes
occurence_of_user_regexes = []
for regex in user_defined_regexes:
    occurence_of_user_regexes.append([regex, 0])

for i in range(len(user_defined_regexes)):
    for j in range(len(list_of_words_found)):
        if list_of_words_found[j][0] == user_defined_regexes[i]:
            occurence_of_user_regexes[i][1] = list_of_words_found[j][1]
            break
if print_user_defined_regexes == True:
    for user_regex, occurence in occurence_of_user_regexes:
        print(user_regex, "occured", occurence, "times")



# Shows all words found
if print_found_words == True:
    for n in range(len(list_of_words_found)):
        print(list_of_words_found[n][0])


# Shows all emails found
if len(list_of_emails_found) == 0:
    print("\nDidn't find any emails")
else:
    print("\nNumber of emails found:", len(list_of_emails_found))
    if print_found_emails is True:
        print("Emails found:")
        for email in list_of_emails_found:
            print(email)



# Shows all phone numbers found
if len(list_of_phone_numbers_found) == 0:
    print("\nDidn't find any phone numbers")
else:
    print("\nNumber of phone numbers found:", len(list_of_phone_numbers_found))
    if print_found_phone_numbers is True:
        print("Phone numbers found:")
        for number in list_of_phone_numbers_found:
            print(number)



# Shows the most frequently used words
list_of_words_found = sorted(list_of_words_found, key=lambda l:l[1], reverse=True)
if print_most_frequently_used_words == True:
    print("\n")
    if len(list_of_words_found) < 10:
        for n in range(len(list_of_words_found)):
            print("\"", list_of_words_found[n][0], "\"", " occured ", list_of_words_found[n][1], " times", sep="")
    else:
        for n in range(10):
            print("\"", list_of_words_found[n][0], "\"", " occured ", list_of_words_found[n][1], " times", sep="")
    print("\n")



# Shows all comments found
print("\nFound", len(list_of_comments_found), "comments")
if print_comments_found == True:
    for n in range(len(list_of_comments_found)):
        print("Comment: ", "\"", list_of_comments_found[n][0], "\"\n", "occured on line ", list_of_comments_found[n][1], " at url\n", list_of_comments_found[n][2], sep="", end="\n\n")














print("\n\n\n--------------------\n\nProgram finished\n\n\n")












"""
To do:
- Validere ekte telefonnumre
    - Jeg får forholde meg til kun norske numre enn så lenge
    - Numre som begynner på 00 i stedet for +

- Inkludere flere bokstaver når man leter etter ord?
    - ü é osv.



"""







# Placeholder
