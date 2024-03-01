from colorama import Fore, Back

CYPHERTEXT_LOCATION = "input\CYPHERTEXT.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram 83-Alph StatProgPerm.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram simpleAlph StatProgPerm.txt"

MINIMUM_PATTERN_SIZE=4  # this specifies the minimum amount of Gaps that a pattern consists of.

# This dictionary decides the color-coding for each GapSize:
GAPCOLORS = {0: Back.LIGHTMAGENTA_EX,
             1: Back.LIGHTGREEN_EX,
             2: Back.LIGHTBLUE_EX,
             3: Back.RED,
             4: Back.YELLOW,
             5: Back.MAGENTA,
             6: Back.CYAN,
             7: Back.GREEN,
             8: Back.LIGHTRED_EX,
             9: Back.LIGHTBLACK_EX,
             10: Back.LIGHTBLACK_EX,
             11: Back.LIGHTBLACK_EX,
             12: Back.LIGHTBLACK_EX,
             13: Back.LIGHTBLACK_EX,
             14: Back.LIGHTBLACK_EX,
             15: Back.LIGHTBLACK_EX,
             16:Back.LIGHTBLACK_EX,
             17:Back.LIGHTBLACK_EX,
             18:Back.LIGHTBLACK_EX,
             19:Back.LIGHTBLACK_EX,
             20:Back.LIGHTBLACK_EX,
             21:Back.LIGHTBLACK_EX,
             22:Back.LIGHTBLACK_EX,
             23:Back.LIGHTBLACK_EX,
             24:Back.LIGHTBLACK_EX,
             }