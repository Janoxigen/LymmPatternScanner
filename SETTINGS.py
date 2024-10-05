from colorama import Fore, Back, Style

CYPHERTEXT_LOCATION = "input\CYPHERTEXT.txt"
CYPHERTEXT_LOCATION = "input\CYPHERTEXT EYES RAW.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT Lymm GroupCTAK fittnessgram.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram 83-Alph StatProgPerm.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram simpleAlph StatProgPerm.txt"

PLAINTEXT_LOCATION = "input\PLAINTEXT.txt"

MINIMUM_PATTERN_SIZE=2  # this specifies the minimum amount of Gaps that a pattern consists of.  (don't set <2 because.... that's not even a Pattern bro)
ALIGN_ISOMORPHS=True   # if TRUE, it prints the Isomorphs so that the patternMarkings are all aligned.
MINIMUM_GROUPSIZE=2     # this specifies the minimum amount of times that each isomorph needs to happen in the ciphertext to be considered interesting.     (don't set <2 because.... if the Pattern only appears once then why even care about it?)
REMOVE_SPACEBARS=False  # self-explanatory.

# If this is TRUE:
PRINT_ONE_CIPHERTEXT_PER_LYMMGROUP=True
# , it will print every Isomorph-Group into one Ciphertext EACH.
# Note that this overrides settings like [align_isomorphs] or [onlyPrintMarkedLines].
# (This setting doesn't work with the new [stringPattern]-class, because i haven't implemented it (yet).)

# if TRUE, it will do one final Print where it stuffs ALL LymmGroups into one Ciphertext. Therefore you should expect huge overlap.
# The print happens after the test_smart_scan().
# The test test_pattern_scanning_REWORKED() does NOT support this final print, because i haven't implemented it (yet?).
PRINT_ALL_GROUPS_INTO_ONE_CIPHERTEXT_AT_END=False

WRITETOFILE=True  # if TRUE, the programm will write some of the colored outputs into a txt-file that can be printed later to re-create the coloring.
OUTPUT_LOCATION="input\OUTPUT.txt"

# This dictionary decides the color-coding for each GapSize:
GAPCOLORS = {0: Back.LIGHTBLACK_EX,
             1: Back.LIGHTGREEN_EX,
             2: Back.LIGHTBLUE_EX+Fore.LIGHTWHITE_EX,
             3: Back.RED,
             4: Back.YELLOW,
             5: Back.MAGENTA+Fore.LIGHTWHITE_EX,
             6: Back.CYAN+Fore.LIGHTWHITE_EX,
             7: Back.GREEN+Fore.LIGHTWHITE_EX,
             8: Back.LIGHTRED_EX,
             9: Back.BLUE+Fore.LIGHTWHITE_EX,
             10: Back.LIGHTYELLOW_EX,
             11: Back.LIGHTBLACK_EX,
             12: Back.MAGENTA+Fore.LIGHTWHITE_EX,
             13: Back.LIGHTBLACK_EX,
             14: Back.LIGHTBLACK_EX,
             15: Back.LIGHTBLACK_EX,
             16:Back.LIGHTCYAN_EX,
             17:Back.LIGHTBLACK_EX,
             18:Back.LIGHTBLACK_EX,
             19:Back.LIGHTBLACK_EX,
             20:Back.LIGHTBLACK_EX,
             21:Back.LIGHTBLACK_EX,
             22:Back.LIGHTBLACK_EX,
             23:Back.LIGHTBLACK_EX,
             24:Back.LIGHTMAGENTA_EX,
             25: Back.LIGHTBLACK_EX,
             26: Back.LIGHTBLACK_EX,
             27: Back.LIGHTBLACK_EX,
             28: Back.LIGHTBLACK_EX,
             29: Back.LIGHTBLACK_EX,
             31: Back.LIGHTBLACK_EX,
             32: Back.LIGHTBLACK_EX,
             33: Back.LIGHTBLACK_EX,
             34: Back.LIGHTBLACK_EX,
             }
# all bigger gapsizes will have a Grey backGround:
for i in range(34,100):
    GAPCOLORS[i]=Back.LIGHTBLACK_EX

BlackLetters = False  # This setting makes all the letters black, so they stand out more on the bright backgrounds.
if BlackLetters:
    for key in GAPCOLORS.keys():
        GAPCOLORS[key] = GAPCOLORS[key]+Fore.BLACK
