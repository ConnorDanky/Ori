import random
import re


def markdown_escape(text: str):
    return re.sub(r"([_*~`|])", r"\\\g<1>", text)


# Generate an array from _min to _max
def range_array(_min, _max):
    array = []
    for x in range(_min, _max + 1):
        array.append(x)
    return array

# Pluralize a string - written by connor totally not copied from akoot ;)
def pluralize(count:int, test:str):
    if count == 1:
        return text
    else:
        return text + 's'


# Generate a random string
def random_string(length, spaces=False, special=False, numbers=False, capitals=True, lowercase=True):
    string = ""

    # Only compute if at least one flag is True, otherwise it will loop indefinitely
    if spaces or special or numbers or capitals or lowercase:

        excluded = []

        # Exclude spaces
        if not spaces:
            excluded.extend(range_array(32, 32))

        # Exclude spacial characters
        if not special:
            excluded.extend(range_array(33, 47))
            excluded.extend(range_array(58, 64))
            excluded.extend(range_array(91, 96))

        # Exclude numbers
        if not numbers:
            excluded.extend(range_array(48, 57))

        # Exclude capital characters
        if not capitals:
            excluded.extend(range_array(65, 90))

        # Exclude lowercase characters
        if not lowercase:
            excluded.extend(range_array(97, 122))

        # Generate a random string
        for i in range(length):

            while True:
                # Generate a random character with ASCII code from 32 to 122
                c = random.randrange(32, 122)

                # If the generated character is not part of the excluded array, stop looping
                if c not in excluded:
                    break

            # Add the generated character to the string
            string += chr(c)
            string = markdown_escape(string)

    return string


def upper(text: str):
    if len(text) > 0:
        if len(text) >= 2:
            return text[0].upper() + text[1:]
        else:
            return text[0].upper()
    else:
        return text
