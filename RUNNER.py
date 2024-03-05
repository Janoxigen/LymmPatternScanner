
"""
EXPLANATION:
Run this file for an example usage of the Scanner.
You can change some settings in the SETTINGS.PY file.
"""


from Pattern_scanner import Pattern_scanner, multiLymmPattern


def test_multimarking(useFewerGapColorings=False, onlyMarkThisGapSize=None):
    """
    :param: useFewerGapColorings: if TRUE, it will remove all GapColors for Gaps >11.
    :param: onlyMarkThisGapSize: if set to an integer, it will only mark that specific gapSize (overriding the above [fewerColors] parameter).
    """
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
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
    print("----------------------------------------")
    print("------ALL Groups of LymmPatterns:-------")
    print("----------------------------------------")

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    f = open(PLAINTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    plaintext = f.read()

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
            break
        print(f"Searching all {len(allPatternsList)} smaller Groups for redundancy against current Groupsize...")
        newAllPatternsList=biggerPatternsList.copy()
        oldPattern: multiLymmPattern
        for oldPattern in allPatternsList:
            patternIsOvershadowed=False
            for newPattern in biggerPatternsList:
                if oldPattern.samePattern(newPattern):
                    patternIsOvershadowed=True
                    continue
            if not patternIsOvershadowed:
                newAllPatternsList.append(oldPattern)
        allPatternsList=newAllPatternsList
        print(f"done! {len(allPatternsList)} satisfying Patterns remain.")
        groupSize +=1
        previous_LymmPatterns = biggerPatternsList

    # ---- print all the found Patterns ----
    chosenText = cyphertext
    # chosenText=plaintext  # by sneakily using the plaintext instead of the ciphertext, we can visualize where the LymmPatterns would be placed on the plaintext.
    for patternID,pattern in enumerate(allPatternsList):
        print(f'{Fore.RED}GROUPSIZE= {pattern.groupSize()} {Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}  {patternID=}{Fore.RESET}')
        #The following two Flags DO NOT WORK if [allIntoOneCiphertext] is enabled:
        #   onlyPrintmarkedLines
        #   alignIsomorphs
        pattern.print_pattern(chosenText, GAPCOLORS, onlyPrintmarkedLines=onlyPrintmarkedLines,
                              alignIsomorphs=ALIGN_ISOMORPHS, allIntoOneCiphertext=PRINT_ONE_CIPHERTEXT_PER_LYMMGROUP)

    if PRINT_ALL_GROUPS_INTO_ONE_CIPHERTEXT_AT_END:
        print("------------------------------------------------------")
        print("------ ALL Groups stuffed into one Ciphertext: -------")
        print("------------------------------------------------------")
        colorCodedGapSizeStrings = [f"{GAPCOLORS[gapSize]}{gapSize}{Style.RESET_ALL}" for gapSize in GAPCOLORS.keys()]
        niceStringed = ",".join(colorCodedGapSizeStrings)
        print(f"used GapSizes={niceStringed}")
        print("")  # Linebreaker

        onlySelectedPatterns=True
        if onlySelectedPatterns:
            #(I selected these Patterns of the Eyes cuz they are the most insteresting.)
            selectedPatternIDs = [0,1,2,3,  5,  7,  9,10,11,12,  14,15,  18]
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
    print("--------------------------------------------")
    print("---------MANUALLY MARKED PATTERNS:----------")
    print("--------------------------------------------")

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()

    patternList=[]

    structureString = "^---^-T---^---T--7---7"
    pos = 56
    msgDescrs = [(3,0)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "^---^------------7---7"
    pos = 56
    msgDescrs = [(4,8)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "^---^-X----E-E---7X--7"
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
    structureString = "----k--\---O-k--\---O"
    pos = 0
    msgDescrs = [(4,0)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "@----------@"
    pos = 36
    msgDescrs = [(5,0),(6,1),(7,3),(8,2)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "@----------@%+OMZdeo9FMiOd"  # Note: this also shows that the structureString ignores all nonReeating Letters.
    pos = 36
    msgDescrs = [      (6,1),(7,3),(8,2)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "V---V"
    pos = 35
    msgDescrs = [(6,0),(7,1),(8,0)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "M---o--M--------o"
    pos = 51
    msgDescrs = [      (6,1),(7,3)      ]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))
    structureString = "M---o--M-----M---"
    pos = 51
    msgDescrs = [      (6,1)      ,(8,2)]
    patternList.append(multiLymmPattern.create_LymmPattern_from_structureString(structureString, pos, msgDescrs))

    Pattern_scanner.print_all_into_one_ciphertext(cyphertext, patternList, GAPCOLORS)

    verbose = False
    if verbose:
        for pattern in patternList:
            print(f'{Fore.RED}GROUPSIZE= {pattern.groupSize()} {Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')


from SETTINGS import *

test_multimarking(useFewerGapColorings=True)
test_multimarking(onlyMarkThisGapSize=2)  #(this works too)
test_alignment_marker()
test_manually_creating_markings()
test_pattern_scanning_smart(onlyPrintmarkedLines=True)
