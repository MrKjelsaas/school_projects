from random import randint

def fillBoardWithMines(inputBoard, minesInput):

    height = len(inputBoard)
    width = len(inputBoard[0])

    # Fills the board with mines
    for mine in range(minesInput):
        inputBoard[randint(0, height-1)][randint(0, width-1)] = "*"

    sum = 0
    for i in range(height):
        for j in range(width):
            if inputBoard[i][j] == "*":
                sum += 1

    # Adds another mine in case we places two on top of each other
    while sum < minesInput:
        inputBoard[randint(0, height-1)][randint(0, width-1)] = "*"
        sum = 0
        for i in range(height):
            for j in range(width):
                if inputBoard[i][j] == "*":
                    sum += 1

    # Counts neighboring mines
    for x in range(height):
        for y in range(width):
            if inputBoard[x][y] != "*":
                sum = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if 0 <= (x + dx) < height:
                            if 0 <= (y + dy) < width:
                                if inputBoard[x+dx][y+dy] == "*":
                                    sum += 1

                inputBoard[x][y] = sum



    return inputBoard

def show(inputBoard): # Prints the board in a prettier way than just print(board)
    for i in range(len(inputBoard)):
        for j in range(len(inputBoard[0])):
            print(inputBoard[i][j], end="")
        print("")





print("\nWelcome to Minesweeper beta!\n")

playerWantsToPlay = True
while playerWantsToPlay == True:
    print("\nStarting new round")

    boardWidth = int(input("Enter width of board: "))
    boardHeight = int(input("Enter height of board: "))
    numberOfMines = int(input("Enter number of mines: "))

    board = [["?"]*boardWidth for _ in range(boardHeight)] # The board that the player sees
    solvedBoard = [["?"]*boardWidth for _ in range(boardHeight)] # The revealed board with mine indicator (*)
    solutionBoard = [["?"]*boardWidth for _ in range(boardHeight)] # The solution the player hopes to achieve

    solvedBoard = fillBoardWithMines(solvedBoard, numberOfMines)

    for i in range(boardHeight):
        for j in range(boardWidth):
            if solvedBoard[i][j] == "*":
                solutionBoard[i][j] = "?"
            else:
                solutionBoard[i][j] = solvedBoard[i][j]



    gameOver = False
    while gameOver == False:
        print("")
        show(board)
        print("")

        validInput = False
        widthInput = int(input("Enter width to guess: "))
        heightInput = int(input("Enter height to guess: "))
        if 0 < widthInput <= boardWidth:
            if 0 < heightInput <= boardHeight:
                validInput = True
        if validInput == False:
            print("Invalid input\n")

        elif validInput == True:
            if solvedBoard[boardHeight-heightInput][widthInput-1] == "*":
                gameOver = True
                print("You hit a mine!\nGame over\n")
                print("")
                show(solvedBoard)
                print("")

                questionAnswered = False
                while questionAnswered == False:
                    playAgainString = input("Would you like to play again? [yes/no] ")
                    if playAgainString.lower() == "yes":
                        playerWantsToPlay = True
                        questionAnswered = True
                    elif playAgainString.lower() == "no":
                        questionAnswered = True
                        playerWantsToPlay = False
                        print("Thank you for playing!\nNow exiting...\n")
                    else:
                        print("Sorry, I didn't understand that")

            else:
                board[boardHeight-heightInput][widthInput-1] = solutionBoard[boardHeight-heightInput][widthInput-1]
                if board == solutionBoard:
                    gameOver = True
                    print("Congratulations! You won!\nGame over\n")
                    print("")
                    show(solvedBoard)
                    print("")

                    questionAnswered = False
                    while questionAnswered == False:
                        playAgainString = input("Would you like to play again? [yes/no] ")
                        if playAgainString.lower() == "yes":
                            playerWantsToPlay = True
                            questionAnswered = True
                        elif playAgainString.lower() == "no":
                            questionAnswered = True
                            playerWantsToPlay = False
                            print("Thank you for playing!\nNow exiting...\n")
                        else:
                            print("Sorry, I didn't understand that")
