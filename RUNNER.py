
"""
EXPLANATION:
Run this file for an example usage of the Scanner.
You can change some settings in the SETTINGS.PY file.
"""


from Pattern_scanner import Pattern_scanner

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

def test_pattern_scanning_nGroups(minimumPatternComplexity=2, onlyPrintmarkedLines=False):
    """
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
                                                                   minimumPatternSize=minimumPatternComplexity,
                                                                   verbose=True)

    print(f"found {len(allPatternsList)} satisfying Patterns. diving into unbroken clusters...")
    validPatternsList = Pattern_scanner.divide_patterns_into_unbroken_clusters(cyphertext,
                                                                               gapSizes=list(GAPCOLORS.keys()),
                                                                               PatternsList=allPatternsList,
                                                                               minClusterSize=minimumPatternComplexity,
                                                                               gapColorDict=GAPCOLORS,
                                                                               verbose=False)

    print(f"done! found {len(validPatternsList)} satisfying Patterns.")
    # ---- print all the found Patterns ----
    chosenText=cyphertext
    #chosenText=plaintext  # by sneakily using the plaintext instead of the ciphertext, we can visualize where the LymmPatterns would be placed on the plaintext.
    for pattern in validPatternsList:
        print(f'{Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
        pattern.print_pattern(chosenText, GAPCOLORS, onlyPrintmarkedLines=onlyPrintmarkedLines, alignIsomorphs=ALIGN_ISOMORPHS)


from SETTINGS import *
print("------------------------------")
print("-------------GAPS:------------")
print("------------------------------")
test_multimarking(useFewerGapColorings=True)
print("------------------------------")
print("---------ALIGNMENTS:----------")
print("------------------------------")
test_alignment_marker()
print("-----------------------------------------------")
print("------ALL N-Size Groups of LymmPatterns:-------")
print("-----------------------------------------------")
test_pattern_scanning_nGroups(minimumPatternComplexity=MINIMUM_PATTERN_SIZE,
                              onlyPrintmarkedLines=True)

