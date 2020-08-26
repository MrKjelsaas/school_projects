def task1():
    username = input("What's your name? ")
    number_of_cookies = int(input("How many cookies would you like to have? "))
    print("Hi " + username + ", here are your cookies: " + number_of_cookies*"cookie ")


def task2():
    username = input("What's your name? ")
    number_of_cookies = int(input("How many cookies would you like to have? "))

    if 1 <= number_of_cookies < 10:
        print("Are you sure it's enough?")
    elif 10 <= number_of_cookies < 20:
        print("I agree cookies are delicious!")
    elif 20 <= number_of_cookies <= 50:
        print("Be careful, it's getting too much")
    elif number_of_cookies > 50:
        print("No way, it's getting too much")
        number_of_cookies = 50
    else:
        print("Something must be wrong, I give you 10 cookies")
        number_of_cookies = 10

    print("Hi " + username + ", here are your cookies: " + number_of_cookies*"cookie ")


def task3():
    amount_of_numbers = int(input("How many numbers do you have? "))
    if amount_of_numbers <= 0:
        print("Invalid amount of numbers")
    else:
        total = 0
        for n in range(amount_of_numbers):
            total += int(input("What is the " + str(n+1) + ". number? "))
        average = total / amount_of_numbers
        print("The average is: %.2f" % average)


task1()
task2()
task3()
