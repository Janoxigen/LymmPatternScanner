from colorama import Fore, Back

CYPHERTEXT_LOCATION = "input\CYPHERTEXT.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram 83-Alph StatProgPerm.txt"
#CYPHERTEXT_LOCATION = "input\CYPHERTEXT FittnessGram simpleAlph StatProgPerm.txt"

PLAINTEXT_LOCATION = "input\PLAINTEXT.txt"

MINIMUM_PATTERN_SIZE=2  # this specifies the minimum amount of Gaps that a pattern consists of.  (don't set <2 because.... that's not even a Pattern bro)
ALIGN_ISOMORPHS=False   # if TRUE, it prints the Isomorphs so that the patternMarkings are all aligned.
MINIMUM_GROUPSIZE=2     # how many Isomorphs are in each IsomorphGroup AT LEAST.  tuples? triples? quadruples?     (don't set <2 because.... if the Pattern only appears once then why even care about it?)

# If this is TRUE:
PRINT_ALL_ISOMORPHS_INTO_ONE_CIPHERTEXT=True
# , it will print every Isomorph-Group into one Ciphertext EACH.
# Note that this overrides settings like [align_isomorphs] or [onlyPrintMarkedLines].


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

# ---- DEPRECATED ---
# (not really deprecated but useless since the "smart"-Version doesn't use it.)
#GROUPSIZE=3             # how many Isomorphs are in each IsomorphGroup.  tuples? triples? quadruples?