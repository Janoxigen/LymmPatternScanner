
"""
EXPLANATION:
Run this file for an example usage of the Scanner.
You can change some settings in the SETTINGS.PY file.
"""


from Pattern_scanner import Pattern_scanner, multiLymmPattern
from SETTINGS import *
from internal_tools import *
import re


def test_multimarking(useFewerGapColorings=False, onlyMarkThisGapSize=None):
    """
    :param: useFewerGapColorings: if TRUE, it will remove all GapColors for Gaps >11.
    :param: onlyMarkThisGapSize: if set to an integer, it will only mark that specific gapSize (overriding the above [fewerColors] parameter).
    """
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    if REMOVE_SPACEBARS is True:
        cyphertext = re.sub(' ', '', cyphertext)
    cypherlines = cyphertext.split("\n")

    if onlyMarkThisGapSize is not None:
        print("----------------------------------")
        print("----------SINGLE GAPSIZE----------")
        print("----------------------------------")
        gapColorDict = {onlyMarkThisGapSize: Back.LIGHTBLUE_EX}  # (this is a quick way to mark only one specific GapSize by overwriting the GapColorDict temporarily)
    else:
        print("------------------------------")
        print("---------ALL GAPSIZES:--------")
        print("------------------------------")
        if useFewerGapColorings:
            #(make the coloring less cluttered by removing some)
            maxColoringGapSize=11
            print(f"trimming down GapColoringDict to only Gapsizes smaller than {maxColoringGapSize}")
            gapColorDict={}
            for gapSize in GAPCOLORS.keys():
                if gapSize<=maxColoringGapSize:
                    gapColorDict[gapSize]=GAPCOLORS[gapSize]
        else:
            gapColorDict=GAPCOLORS

    colorCodedGapSizeStrings = [f"{gapColorDict[gapSize]}{gapSize}{Style.RESET_ALL}" for gapSize in gapColorDict.keys()]
    niceStringed = ",".join(colorCodedGapSizeStrings)
    print(f"used GapSizes={niceStringed}")

    for line in cypherlines:
        Pattern_scanner.print_all_gapsizes_marked(line, gapColorDict)


def test_alignment_marker():
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    if REMOVE_SPACEBARS is True:
        cyphertext = re.sub(' ', '', cyphertext)
    print("------------------------------")
    print("---------ALIGNMENTS:----------")
    print("------------------------------")
    Pattern_scanner.print_alignments_marked(cyphertext)


def test_pattern_scanning_smart(onlyPrintmarkedLines=False):
    """
    Smart version of the nGroup-scanning.
    This Version scanns for bigger groups until no more found.
    Any duplicate Patterns overshadowed by a bigger group are ignored.

    :param: minimumPatternComplexity: It will only accept Patterns with at least X-many LymmPairs.
    :param: onlyPrintmarkedLines: If TRUE, it will only print the line where the LymmPatterns happen, instead ofthe entire ciphertext.  Usefull to avoid Clutter.
    """
    output("----------------------------------------")
    output("------ALL Groups of LymmPatterns:-------")
    output("----------------------------------------")

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    f = open(PLAINTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    #f = open(PLAINTEXT_LOCATION, "r",encoding="utf-16")  # (sometimes we need to specify the correct encoding)
    plaintext = f.read()

    if REMOVE_SPACEBARS is True:
        cyphertext = re.sub(' ', '', cyphertext)

    allPatternsList = []
    groupSize=MINIMUM_GROUPSIZE
    previous_LymmPatterns=None
    while True:
        biggerPatternsList = Pattern_scanner.find_all_LymmPattern_nGroups(desired_groupsize=groupSize,
                                                                          cyphertext_whole=cyphertext,
                                                                          gapSizes=list(GAPCOLORS.keys()),
                                                                          minimumPatternSize=MINIMUM_PATTERN_SIZE,
                                                                          previous_LymmPatterns=previous_LymmPatterns,
                                                                          verbose=False)
        print(f"found {len(biggerPatternsList)} Patterns of Groupsize={groupSize}. diving into unbroken clusters...")
        biggerPatternsList = Pattern_scanner.divide_patterns_into_unbroken_clusters(cyphertext,
                                                                                   PatternsList=biggerPatternsList,
                                                                                   minClusterSize=MINIMUM_PATTERN_SIZE,
                                                                                   gapColorDict=GAPCOLORS,
                                                                                   verbose=False)

        print(f"done! found {Fore.BLUE}{len(biggerPatternsList)}{Fore.RESET} satisfying Patterns of {Fore.BLUE}Groupsize={groupSize}{Fore.RESET}.")
        if len(biggerPatternsList) <=0:
            print(f"NO Groups of size {groupSize} found, finishing scan.")
            if previous_LymmPatterns is not None:
                allPatternsList.extend(previous_LymmPatterns)
            if previous_LymmPatterns is None:
                print(f"Not even one pattern found.")
                return
            break

        if previous_LymmPatterns is not None:
            print(f"Searching all previous {len(previous_LymmPatterns)} Groups of size {groupSize - 1} for redundancy against current Groupsize...")

            # NOTE: I rewrote this part so that it only checks the previous bigPatGroup, since all the older(smaller) ones are clearly unique and cannot collide anymore.
            #   BUT that means that patterns only get added during the NEXT ITERATIONS overshadow-check.
            #   That means that on the final abort, the entire prevGroup-List must be added.
            def patternIsOvershadowed(oldPattern: multiLymmPattern, bigPatList: list[multiLymmPattern]) -> bool:
                for newPattern in bigPatList:
                    if oldPattern.samePattern(newPattern):
                        return True
                return False

            filtered_prevPatternList = [entry for entry in previous_LymmPatterns if not patternIsOvershadowed(entry, biggerPatternsList)]
            print(f"done! {len(filtered_prevPatternList)} satisfying Patterns remain.")
            allPatternsList.extend(filtered_prevPatternList)

        groupSize +=1
        previous_LymmPatterns = biggerPatternsList

    # ---- print all the found Patterns ----
    interestingIDs=[]  # if this list is empty, it will print all patterns.
    #interestingIDs=[0,1,2,3,  5,  7,  9,10,11,12,  14,15,16,  18]
    if len(interestingIDs) !=0:
        allPatternsList = [entry for ID, entry in enumerate(allPatternsList) if ID in interestingIDs]

    chosenText = cyphertext
    # chosenText=plaintext  # by sneakily using the plaintext instead of the ciphertext, we can visualize where the LymmPatterns would be placed on the plaintext.
    allPatternsList = sorted(allPatternsList, key=lambda pattern: pattern.groupSize(), reverse=True)  # sort all the groups small2big.
    for patternID,pattern in enumerate(allPatternsList):
        output(f'{Fore.RED}GROUPSIZE= {pattern.groupSize()} {Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}  {patternID=}{Fore.RESET}')
        #The following two Flags DO NOT WORK if [allIntoOneCiphertext] is enabled:
        #   onlyPrintmarkedLines
        #   alignIsomorphs
        pattern.print_pattern(chosenText, GAPCOLORS, onlyPrintmarkedLines=onlyPrintmarkedLines,
                              alignIsomorphs=ALIGN_ISOMORPHS, allIntoOneCiphertext=PRINT_ONE_CIPHERTEXT_PER_LYMMGROUP)
        output("")  # linebreaker

    if PRINT_ALL_GROUPS_INTO_ONE_CIPHERTEXT_AT_END:
        output("------------------------------------------------------")
        output("------ ALL Groups stuffed into one Ciphertext: -------")
        output("------------------------------------------------------")
        colorCodedGapSizeStrings = [f"{GAPCOLORS[gapSize]}{gapSize}{Style.RESET_ALL}" for gapSize in GAPCOLORS.keys()]
        niceStringed = ",".join(colorCodedGapSizeStrings)
        output(f"used GapSizes={niceStringed}\n")

        onlySelectedPatterns=False
        if onlySelectedPatterns:
            selectedPatternIDs = [0,1,2,3,  5,  7,  9,10,11,12,  14,15,  18]  # (This is just some example selection.)
            allPatternsList = [allPatternsList[ID] for ID in selectedPatternIDs]
        Pattern_scanner.print_all_into_one_ciphertext(cyphertext, allPatternsList, GAPCOLORS)


def test_manually_creating_markings():
    """
    Smart version of the nGroup-scanning.
    This Version scanns for bigger groups until no more found.
    Any duplicate Patterns overshadowed by a bigger group are ignored.

    :param: minimumPatternComplexity: It will only accept Patterns with at least X-many LymmPairs.
    :param: onlyPrintmarkedLines: If TRUE, it will only print the line where the LymmPatterns happen, instead ofthe entire ciphertext.  Usefull to avoid Clutter.
    """
    output("--------------------------------------------")
    output("---------MANUALLY MARKED PATTERNS:----------")
    output("--------------------------------------------")

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    if REMOVE_SPACEBARS is True:
        cyphertext = re.sub(' ', '', cyphertext)

    patternList=[]

    if True: # (this [if] is just for folding purposes.)
        structureString = "^---^-T---^---T--7---7"
        pos = 56
        msgDescrs = [(3,0)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "^---^------------7---7"
        pos = 56
        msgDescrs = [(4,8)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "^---^-X----E-E----X---"
        pos = 56
        msgDescrs = [(5,9)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "^--^"
        pos = 96
        msgDescrs = [(3,0),(4,7),(5,23)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = ":-----:"
        pos = 94
        msgDescrs = [(6,0),(7,3),(8,8)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "@----------@"
        pos = 36
        msgDescrs = [(5,0),(6,1),(7,3),(8,2)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "@----------@%+OMZ-eo9FMiOd"  # Note: this also shows that the structureString ignores all nonReeating Letters.
        pos = 36
        msgDescrs = [      (6,1),(7,3),(8,2)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "V---V"
        pos = 35
        msgDescrs = [(6,0),(7,1),(8,0)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "M---o--M--------o"
        pos = 51
        msgDescrs = [(6,1),(7,3)      ]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "M---o--M-----M---"
        pos = 51
        msgDescrs = [(6,1)      ,(8,2)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "kPVW3^`.OSfk%+OMZ-eo9FMiOdRBMn:o"
        pos = 36
        msgDescrs = [(6,1)            ]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
        structureString = "%---------------------------%"
        pos = 70
        msgDescrs = [(6,0),(7,3),(8,2)]
        patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))

    Pattern_scanner.print_all_into_one_ciphertext(cyphertext, patternList, GAPCOLORS)

    verbose = False
    if verbose:
        for pattern in patternList:
            output(f'{Fore.RED}GROUPSIZE= {pattern.groupSize()} {Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
    output(f"{Fore.LIGHTBLACK_EX}{Fore.RESET}")# why is this line here???

if WRITETOFILE:
    # initiate and reset out-file contents.
    f = open(OUTPUT_LOCATION, "w")
    f.close()

test_multimarking(useFewerGapColorings=True)
test_multimarking(onlyMarkThisGapSize=2)  #(this works too)
test_alignment_marker()
test_pattern_scanning_smart(onlyPrintmarkedLines=True)
#test_manually_creating_markings()

