
"""
EXPLANATION:
Run this file for an example usage of the Scanner.
You can change some settings in the SETTINGS.PY file.
"""


from Pattern_scanner import Pattern_scanner, multiLymmPattern


def test_multimarking(useFewerGapColorings=False):
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    cypherlines = cyphertext.split("\n")

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

    print(f"used GapSizes={list(gapColorDict.keys())}")
    for line in cypherlines:
        Pattern_scanner.print_all_gapsizes_marked(line, gapColorDict)


def test_alignment_marker():
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()

    Pattern_scanner.print_alignments_marked(cyphertext)


def test_pattern_scanning_nGroups(onlyPrintmarkedLines=False):
    """
    STILL WORKS BUT WHY WOULD YOU USE IT.
    (it only looks for a specific groupsize, while the smart version finds all groupsizes without duplication.)

    :param: minimumPatternComplexity: It will only accept Patterns with at least X-many LymmPairs.
    :param: onlyPrintmarkedLines: If TRUE, it will only print the line where the LymmPatterns happen, instead ofthe entire ciphertext.  Usefull to avoid Clutter.
    """

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    f = open(PLAINTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    plaintext = f.read()

    allPatternsList = Pattern_scanner.find_all_LymmPattern_nGroups(desired_groupsize=GROUPSIZE,
                                                                   cyphertext_whole=cyphertext,
                                                                   gapSizes=list(GAPCOLORS.keys()),
                                                                   minimumPatternSize=MINIMUM_PATTERN_SIZE,
                                                                   verbose=True)

    print(f"found {len(allPatternsList)} Patterns. diving into unbroken clusters...")
    validPatternsList = Pattern_scanner.divide_patterns_into_unbroken_clusters(cyphertext,
                                                                               gapSizes=list(GAPCOLORS.keys()),
                                                                               PatternsList=allPatternsList,
                                                                               minClusterSize=MINIMUM_PATTERN_SIZE,
                                                                               gapColorDict=GAPCOLORS,
                                                                               verbose=False)

    print(f"done! found {len(validPatternsList)} satisfying Patterns.")
    # ---- print all the found Patterns ----
    chosenText = cyphertext
    # chosenText=plaintext  # by sneakily using the plaintext instead of the ciphertext, we can visualize where the LymmPatterns would be placed on the plaintext.
    for pattern in validPatternsList:
        print(f'{Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
        pattern.print_pattern(chosenText, GAPCOLORS, onlyPrintmarkedLines=onlyPrintmarkedLines,
                              alignIsomorphs=ALIGN_ISOMORPHS)


def test_pattern_scanning_smart(onlyPrintmarkedLines=False):
    """
    Smart version of the nGroup-scanning.
    This Version scanns for bigger groups until no more found.
    Any duplicate Patterns overshadowed by a bigger group are ignored.

    :param: minimumPatternComplexity: It will only accept Patterns with at least X-many LymmPairs.
    :param: onlyPrintmarkedLines: If TRUE, it will only print the line where the LymmPatterns happen, instead ofthe entire ciphertext.  Usefull to avoid Clutter.
    """

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
    for pattern in allPatternsList:
        print(f'{Fore.RED}GROUPSIZE= {pattern.groupSize()} {Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
        #The following two Flags DO NOT WORK if [allIntoOneCiphertext] is enabled:
        #   onlyPrintmarkedLines
        #   alignIsomorphs
        pattern.print_pattern(chosenText, GAPCOLORS, onlyPrintmarkedLines=onlyPrintmarkedLines,
                              alignIsomorphs=ALIGN_ISOMORPHS, allIntoOneCiphertext=PRINT_ALL_ISOMORPHS_INTO_ONE_CIPHERTEXT)


from SETTINGS import *
print("------------------------------")
print("-------------GAPS:------------")
print("------------------------------")
test_multimarking(useFewerGapColorings=True)
print("------------------------------")
print("---------ALIGNMENTS:----------")
print("------------------------------")
test_alignment_marker()
#test_pattern_scanning_nGroups(onlyPrintmarkedLines=True)
print("----------------------------------------")
print("------ALL Groups of LymmPatterns:-------")
print("----------------------------------------")
test_pattern_scanning_smart(onlyPrintmarkedLines=True)
