POSITIONS = list("01234567")
VALUES = list("01")

guesses = [
    ("00000000", 5),
    ("01011010", 5),
    ("01111000", 5),
    ("00111100", 5),
    ("11101011", 5)
]

# Count number of matching positions
def count_correct(guess, option):
    correct = 0
    for g, o in zip(guess, option):
        if g == o:
            correct += 1
    return correct

# recursively create all options, and check if they match the guesses
def check_options(option=""):
    if (len(option) < len(POSITIONS)):
        for val in VALUES:
            check_options(option + val)
    else:
        found = True
        for guess, correct in guesses:
            if count_correct(guess, option) != correct:
                found = False
        if found:
            #print(option)
            print("FOUND")


check_options()
