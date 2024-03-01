
"""
EXPLANATION:
Run this file for an example usage of the Scanner.
You can change some settings in the SETTINGS.PY file.
"""


from Pattern_scanner import Pattern_scanner, LymmPattern

def test_multimarking(useFewerGapColorings=False):
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()
    lines = cyphertext.split("\n")

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
    for line in lines:
        Pattern_scanner.print_all_gapsizes_marked(line, gapColorDict)

def test_alignment_marker():
    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()

    Pattern_scanner.print_alignments_marked(cyphertext)

def test_pattern_scanning_all(minimumPatternComplexity=2, onlyPrintmarkedLines=False):
    """
    :param minimumPatternComplexity: It will only accept Patterns with at least X-many LymmPairs.
    :param onlyPrintmarkedLines: If TRUE, it will only print the line where the LymmPatterns happen, instead ofthe entire ciphertext.  Usefull to avoid Clutter.
    """

    f = open(CYPHERTEXT_LOCATION, "r")  # (the File needs to be in the same folder in a [input] folder)
    cyphertext = f.read()

    allPatternsList:list[LymmPattern] = Pattern_scanner.find_all_Lymm_patterns(cyphertext,
                                                                                  gapSizes = list(GAPCOLORS.keys()),
                                                                                  verbose=True)

    validPatternsList = Pattern_scanner.divide_patterns_into_unbroken_clusters(cyphertext,gapSizes = list(GAPCOLORS.keys()),PatternsList=allPatternsList,minClusterSize=minimumPatternComplexity,gapColorDict=GAPCOLORS,verbose=False)

    print(f"found {len(validPatternsList)} satisfying Patterns.")
    # ---- print all the found Patterns ----
    for pattern in validPatternsList:
        print(f'{Fore.LIGHTBLACK_EX}{pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
        Pattern_scanner.print_Lymm_pattern(cyphertext,
                                           targetPattern=pattern,
                                           gapColorDict=GAPCOLORS,
                                           onlyPrintmarkedLines=onlyPrintmarkedLines)
        #Note: It might be possible to still display all the LymmPairs that were removed during distilling.
        #  But you would need to alter the print_Lymm_pattern() Function to support a secondary GREY pattern
        #  that gets printed first and then overwritten by the distilled Pattern wherever LymmPairs are left.


from SETTINGS import *
print("------------------------------")
print("-------------GAPS:------------")
print("------------------------------")
test_multimarking(useFewerGapColorings=True)
print("------------------------------")
print("---------ALIGNMENTS:----------")
print("------------------------------")
test_alignment_marker()
print("------------------------------")
print("------ALL LYMMPATTERNS:-------")
print("------------------------------")
test_pattern_scanning_all(minimumPatternComplexity=MINIMUM_PATTERN_SIZE,
                          onlyPrintmarkedLines=True)

