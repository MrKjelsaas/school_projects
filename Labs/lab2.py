
def task1():
    days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

    calendar = []
    for i in range(7*24):
        calendar.append("")

    while True:
        print("")
        print("Commands:")
        print("s - Store program")
        print("l - List daily program")
        print("x - Exit\n")

        userInput = input("Choose from the list: ")

        if userInput == "x":
            exit()

        elif userInput == "s":
            inputDay = input("Which day? ")
            inputHour = int(input("What time? "))
            inputString = input("What is the program? ")

            calendar[days.index(inputDay)*24 + inputHour] = inputString

        elif userInput == "l":
            inputDay = input("Which day? ")
            for i in range(24):
                print(str(i) + ":00", calendar[days.index(inputDay)*24 + i])

        else:
            print("Invalid command")



def task2():
    file = open("python.txt", "r")
    fileString = file.read()
    newFileString = ""

    # Remove anything that is not in the alphabet, digits, or spaces
    for character in fileString:
        if character == " ":
            newFileString += character
        elif character.isalnum():
            newFileString += character


    print("Length of fileString: ", len(fileString))
    print("Length of newFileString: ", len(newFileString))

    wordList = newFileString.split(sep=" ")
    setList = set(wordList)

    dictionary = dict.fromkeys(wordList, 0)

    for word in wordList:
        dictionary[word] += 1

    for entry in dictionary:
        if dictionary[entry] > 3:
            print(entry, dictionary[entry])



#task1()
#task2()
