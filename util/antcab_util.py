#antcab cipher encoder/decoder
j = 0

output = ""
letters_ = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

shift1 = 2
shift2 = -13
shift3 = -18

def main():
    global output
    output = ""
    encode = input("Enter your message for encoding:" )
    encode = encode.upper()
    counter = 0
    for i in encode:
        if i == " ":
            output = output + " "
            continue
        if counter == 0:
            pos = finder(i)
            move = pos + shift1
            if move > 25:
                move -= 26
            output = output + letters_[move]
        elif counter == 1:
            pos = finder(i)
            move = pos + shift2
            if move > 25:
                move -= 26
            output = output + letters_[move]
        elif counter == 2:
            pos = finder(i)
            move = pos + shift3
            if move > 25:
                move -= 26
            output = output + letters_[move]
            counter = -1
        counter += 1

    print(output)


def main2():
    global output
    output = ""
    encode = input("Enter your message for decoding:" )
    encode = encode.upper()
    counter = 0
    for i in encode:
        if i == " ":
            output = output + " "
            continue
        if counter == 0:
            pos = finder(i)
            move = (pos - shift1)
            if move > 25:
                move -= 26
            output = output + letters_[move]
        elif counter == 1:
            pos = finder(i)
            move = (pos - shift2)
            if move > 25:
                move -= 26
            output = output + letters_[move]
        elif counter == 2:
            pos = finder(i)
            move = (pos - shift3)
            if move > 25:
                move -= 26
            output = output + letters_[move]
            counter = -1
        counter += 1

    print(output)


def shift():
    global shift1 
    global shift2 
    global shift3
    default = input("Default Key (y/n): ")
    default = default.lower()
    if default == "y":
        shift1 = 2
        shift2 = -13
        shift3 = -18
        return 1
    if default == "n":
        word1 = input("The first key: ")
        word2 = input("The second key: ")
        word1 = word1.upper()
        word2 = word2.upper()

        var1a = finder(word1[0])
        var1b = finder(word1[1])
        var1c = finder(word1[2])
        var2a = finder(word2[0])
        var2b = finder(word2[1])
        var2c = finder(word2[2])

        shift1 = var2a-var1a
        shift2 = var2b-var1b
        shift3 = var2c-var1c

def finder(letter):
    counter = 0
    for i in letters_:
        if i == letter:
            return counter
        else:
            counter += 1
            
def start():
    mode = input("Mode (e/d) - ")
    mode = mode.lower()
    if mode == "e":
        main()
    elif mode == "d":
        main2()


while True:
    shift()
    start()
    print("________________")
