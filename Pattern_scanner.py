
from colorama import Fore, Back, Style
from typing import Union

class LymmPair:
    def __init__(self,index:int,gapsize:int):
                 self.index = index      # (index of the left of the two letters.)
                 self.gapsize = gapsize  # (how many empty spaces are between the two letters.)
                 self.pairOffset  = gapsize+1

    def __str__(self):
        return f"({self.index}:{self.gapsize})"
    def __repr__(self):
        return self.__str__()

class LymmPattern:
    def __init__(self,
                 LymmPairs:list[LymmPair],
                 messageIDs:tuple[int,int],
                 offset:int  # The offset of how much the secondMessages LymmPattern is offset to the right. Can only be positive.
                 ):
        self.LymmPairs = LymmPairs
        self.messageIDs = messageIDs
        self.offset = offset

    def length(self):
        return len(self.LymmPairs)

    def __str__(self):
        return f"<LymmPairs:{self.LymmPairs},  firstMessageID={self.messageIDs[0]},  secndMessageID={self.messageIDs[1]},  offset={self.offset}>"
    def __repr__(self):
        return self.__str__()

#TODO switch to multiLymmPatterns that need to be created during Patterngathering or the LymmPatterns need to store their GapDB-representation too.
class multiLymmPattern:
    def __init__(self,
                 LymmPairs:list[LymmPair],
                 messageDescrs:list[tuple[int,int]],  # for every involved Message we have an (index,offset) Tuple.  (the first offset is always 0)
                 ):
        self.LymmPairs = LymmPairs
        self.messageDescrs = messageDescrs

    def length(self):
        return len(self.LymmPairs)
    def messageCount(self):
        return len(self.messageDescrs)

    def __str__(self):
        MessageDescrStrings=[f"(msgID={descr[0]},offset={descr[1]})" for descr in self.messageDescrs]
        return f"<LymmPairs:{self.LymmPairs}, {MessageDescrStrings}>"
    def __repr__(self):
        return self.__str__()

class Pattern_scanner:

    # DONE, Works---
    @staticmethod
    def find_all_Lymm_patterns(cyphertext_whole: str, gapSizes: list[int], verbose=False) -> Union[LymmPattern,list[LymmPattern]]:
        """
        Searches for all Lymm-Patterns that appear at least twice.
        :param: gapSizes: a list of the Sizes that we want to check
        """
        #############
        # PSEUDOCODE:
        # >Overlay the gap-positions of each pair of messages and take
        #  note if any of those positions overlap.
        # >Repeat step 1 for each possible offset between messages.
        # NOTES:
        # (To prevent duplicate finds, we only check offsets to
        # messages that are "below" the current message or within
        # the same message but "to the right".)
        #############

        # -----------------------
        # ----- PREPARATION -----
        # -----------------------
        cipherLines = cyphertext_whole.split("\n")
        each_lines_GapDB = []  # this will be one entry for each Line-ID, ergo an entry is a list, mapping  position->Gaps
        for lineID in range(0, cipherLines.__len__()):
            currLine = cipherLines[lineID]
            currDB = Pattern_scanner.__gather_gapDB_of_line(currLine, gapSizes)
            each_lines_GapDB.append(currDB)

        totalPatternCount = 0
        allPatternsList = []

        # -----------------------
        # ------- SCANNING ------
        # -----------------------
        for mainLineID in range(0, cipherLines.__len__()):
            mainLines_gapDB = each_lines_GapDB[mainLineID]
            for secondLineID in range(0, cipherLines.__len__()):
                secondLineLen = cipherLines[mainLineID].__len__()
                secondLines_gapDB = each_lines_GapDB[secondLineID]

                startoffset = 0  # the offset can only be positive, but by swapping the roles of main- and secondLine, we do an "inverted" test.
                if secondLineID <= mainLineID:
                    """
                    if we are comparing it to the line itself, we can only scan whatever
                    is to the "right" of what was already scanned. (to prevent self-finds.)
                    
                    This is also a startoffset-adjustment to prevent duplicate finds of zero-offsets between different messages.
                    """
                    startoffset = 1  # (ergo we don't start at 0-Offset)

                for currOffset in range(startoffset, secondLineLen):
                    offsetted_gapDB = secondLines_gapDB[currOffset:]  # we slice off every gap before the offset-index.
                    pattern = Pattern_scanner.__analyze_specific_overlay(mainLines_gapDB, offsetted_gapDB)
                    totalPatternCount +=1
                    newLymmPattern = LymmPattern(pattern, messageIDs=(mainLineID, secondLineID), offset=currOffset)
                    allPatternsList.append(newLymmPattern)
        if verbose:
            print(f"checked a total of {totalPatternCount} Offsets for Lymm Patterns.")
        return allPatternsList

    # DONE, Works---
    @staticmethod
    def __analyze_specific_overlay(first_gapDB: list, second_gapDB: list) -> list[LymmPair]:
        """
        "Overlays" the two given gap-DBs and returns a list of all the overlapping Gaps.
        :returns: LIST of Tuples like this:  [(position, gapSize)]
        """
        resultList = []
        comparelength = min(first_gapDB.__len__(), second_gapDB.__len__())
        for index in range(0, comparelength):  # for all indexes...
            # ...check which of the first DBs gaps at that index are also in the second DB at this index:
            toCheck_gapSizes = first_gapDB[index]
            for size in toCheck_gapSizes:
                if size in second_gapDB[index]:
                    newLymmPair = LymmPair(index, gapsize=size)
                    resultList.append(newLymmPair)
        return resultList

    # DONE, Works---
    @staticmethod
    def __gather_gapDB_of_line(line: str, gapSizes: list[int]) -> list[list[int]]:
        """
        :returns: a LIST, that contains a List of gapSizes at each Positions index
        """
        textlen = line.__len__()
        resultList = []
        for position in range(0, textlen):  # for each letter of the Text...
            currLetter = line[position]
            currPossesGapList = []
            for gapSize in gapSizes:
                gapOffset = gapSize + 1
                if position+gapOffset < line.__len__(): #  if the gap exists looking forward...
                    secondLetter = line[position+gapOffset]
                    if currLetter == secondLetter:
                        currPossesGapList.append(gapSize)
            resultList.append(currPossesGapList)
        return resultList

    # DONE, Works---
    @staticmethod
    def print_Lymm_pattern(cyphertext_whole: str, targetPattern: LymmPattern, gapColorDict: dict, singlePrint=True, onlyPrintmarkedLines=False):
        """
        Prints and marks a singular Lymm-Pattern-Pair.
        """
        mainMessageID = targetPattern.messageIDs[0]
        secondMessageID = targetPattern.messageIDs[1]
        secondMessageOffset = targetPattern.offset
        lines = cyphertext_whole.split("\n")
        # ---- once for every Line involved in the Isomorph: ----
        for currPatternID in [1,2]:
            # ---- Print the entire Ciphertext with only that Pattern marked: ----
            for lineID in range(0, lines.__len__()):
                currLineStr = lines[lineID]

                listified = list(currLineStr)
                firstHit = lineID == mainMessageID
                secndHit = lineID == secondMessageID

                if currPatternID == 1 and firstHit:
                    Pattern_scanner.__mark_one_Lymm_pattern(listified, targetPattern, gapColorDict, maskOffset=0)
                    resultString = "".join(listified)
                    print(resultString)

                if currPatternID == 2 and secndHit:
                    Pattern_scanner.__mark_one_Lymm_pattern(listified, targetPattern, gapColorDict,maskOffset=secondMessageOffset)
                    resultString = "".join(listified)
                    print(resultString)

                if not (firstHit or secndHit):
                    if not onlyPrintmarkedLines:
                        print(currLineStr)

    # DONE, Works---
    @staticmethod
    def __mark_one_Lymm_pattern(listified_text: list, targetPattern: LymmPattern, gapColorDict: dict, maskOffset: int):
        """
        Goes over the provided listified String and adds coloring to all the characters that are in a Gap
        in the provided pattern.

        NOTE:  The listified text needs to match the index-Notation of the pattern:
                If the indexes referr to the position within the entire ciphertext, pass the entire ciphertext.
                If the indexes referr to the position within the SPECIFIC LINE, pass that specific line only.
        """

        def mark_letter(listified_string: list, index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Back.RESET

        pattern = targetPattern.LymmPairs
        for pair in pattern:  # for each Gap, mark both of its letters in the respective color
            leftLetter_pos = pair.index + maskOffset
            gapSize = pair.gapsize
            rightLetter_pos = leftLetter_pos + pair.pairOffset
            colorcode = gapColorDict[gapSize]
            mark_letter(listified_text, leftLetter_pos, colorcode)
            mark_letter(listified_text, rightLetter_pos, colorcode)

    # DONE, Works---
    @staticmethod
    def print_all_gapsizes_marked(text: str, gapColorDict: dict):
        """
        Prints the given Cyphertext-Line and marks the provided Gapsizes in their assigned Colors.
        """
        textlen = text.__len__()
        for position in range(0, textlen):  # for each letter of the Text...
            currLetter = text[position]
            resultColor = ""  # we determine the if it needs to be colored in some gaps color...
            for gapSize in gapColorDict.keys():  # by checking for all gapSizes, whether...
                gapOffset = gapSize + 1
                sizeColor = gapColorDict[gapSize]
                if position - gapOffset >= 0:  # ...the gap indeed exists looking back...
                    lookbackPartner = text[position - gapOffset]
                    if currLetter == lookbackPartner:
                        # resultColor = sizeColor
                        resultColor = sizeColor + Fore.BLACK
                if position + gapOffset < text.__len__():  # ...,or the gap exists looking forward...
                    lookforwardPartner = text[position + gapOffset]
                    if currLetter == lookforwardPartner:
                        # resultColor = sizeColor
                        resultColor = sizeColor + Fore.BLACK
            # print(f"{resultColor}{currLetter}{Back.RESET}", end='')
            print(f"{resultColor}{currLetter}{Fore.RESET}{Back.RESET}", end='')
        print("")

    # DONE, Works---
    @staticmethod
    def print_alignments_marked(cyphertext_whole: str):
        """
        Prints the given Text and marks all the Letters that align with another Lines Letter.
        """
        lines = cyphertext_whole.split("\n")
        SPACING_letter = "°"

        for line in lines:
            for position in range(0, line.__len__()):
                is_aligned = False
                currLetter = line[position]
                if currLetter == SPACING_letter:
                    print(currLetter, end="")
                    continue
                for otherline in lines:
                    if otherline != line:
                        if position < otherline.__len__():
                            otherLetter = otherline[position]
                            if otherLetter == currLetter:
                                is_aligned = True
                                break
                if is_aligned:
                    print(f"{Back.GREEN}{currLetter}{Back.RESET}", end="")
                else:
                    print(currLetter, end="")
            print("")  # a linebreak

    # DONE, Works---
    @staticmethod
    def __mark_one_Lines_GapDB(cipherLine: str, thisLines_gapDB:list[list[int]], gapColorDict: dict, maskOffset: int)->str:
        """
        Goes over the provided listified String and adds coloring to all the characters that are in a Gap
        in the provided gapDB.

        NOTE:  The listified text needs to match the index-Notation of the pattern:
                If the indexes referr to the position within the entire ciphertext, pass the entire ciphertext.
                If the indexes referr to the position within the SPECIFIC LINE, pass that specific line only.
        """

        def mark_letter(listified_string: list, index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Back.RESET

        listified_text=list(cipherLine)
        for index, indexes_gapSizeList in enumerate(thisLines_gapDB):
            leftLetter_pos = index + maskOffset
            for gapSize in indexes_gapSizeList:
                rightLetter_pos = leftLetter_pos + gapSize+1
                colorcode = gapColorDict[gapSize]
                mark_letter(listified_text, leftLetter_pos, colorcode)
                mark_letter(listified_text, rightLetter_pos, colorcode)
        return "".join(listified_text)

    # DONE, Works---
    @staticmethod
    def divide_patterns_into_unbroken_clusters(cyphertext_whole: str,
                                               gapSizes: list[int],
                                               PatternsList:list[LymmPattern],
                                               minClusterSize=2,
                                               gapColorDict: dict=None,
                                               verbose=False
                                               )->list[LymmPattern]:
        """
        (doesn't actually edit the original list nor the Patterns within.)

        Goes over all LymmPatterns and if there is any patternbreaking LymmPair, the Patterns is split into unbroken clusters.
        Also removes any LymmPairs that fully contain a patternbreaking LymmPair.
        """
        # ----- prepare the GapDBs -----
        cipherLines = cyphertext_whole.split("\n")
        each_lines_GapDB = []  # this will be one entry for each Line-ID, ergo an entry is a list, mapping  position->Gaps
        for lineID in range(0, cipherLines.__len__()):
            currLine = cipherLines[lineID]
            currDB = Pattern_scanner.__gather_gapDB_of_line(currLine, gapSizes)
            each_lines_GapDB.append(currDB)

        def generate_breaking_gapDB(gapDB_A:list[list[int]], gapDB_B:list[list[int]], offset:int)->list[list[int]]:
            """
            Returns a list of lists.
            For every position (accounting for offset), a list of all the gaps that aren't in BOTH gapDBs at that position.
            (Assumes that the offset is possible with those gapDBs)
            """
            resultDB = []
            maxScanIndex = min(len(gapDB_A),  len(gapDB_B)-offset)
            overall_onlyA=[]
            overall_onlyB=[]
            for index in range(maxScanIndex):
                gapSizeList_A = gapDB_A[index]
                gapSizeList_B = gapDB_B[index+offset]
                onlyA = [gapSize for gapSize in gapSizeList_A if gapSize not in gapSizeList_B]
                onlyB = [gapSize for gapSize in gapSizeList_B if gapSize not in gapSizeList_A]
                allUnique = onlyA.copy()

                overall_onlyA.append(onlyA)
                overall_onlyB.append(onlyB)

                allUnique.extend(onlyB)
                resultDB.append(allUnique)

            if verbose:
                if superVerbose:
                    firstMessageID = pattern.messageIDs[0]
                    secndMessageID = pattern.messageIDs[1]
                    firstMessage_marked = Pattern_scanner.__mark_one_Lines_GapDB(cipherLine=cipherLines[firstMessageID],
                                                                                 thisLines_gapDB=overall_onlyA,
                                                                                 gapColorDict=gapColorDict,
                                                                                 maskOffset=0)
                    secndMessage_marked = Pattern_scanner.__mark_one_Lines_GapDB(cipherLine=cipherLines[secndMessageID],
                                                                                 thisLines_gapDB=overall_onlyB,
                                                                                 gapColorDict=gapColorDict,
                                                                                 maskOffset=0)
                    print("------------------ breakPairs start ------------------")
                    print(firstMessage_marked)
                    print(secndMessage_marked)
                    print("////////////////// breakPairs end //////////////////")

            return resultDB

        def split_clusters_using_Breakerpair(clustersList:list[list[LymmPair]], breakerPair: LymmPair)->list[list[LymmPair]]:
            """
            For every cluster, this creates a "left" and "right" side cluster based on the breakerPair.
            Btw, this (as a sideffect) filters out all LymmPairs that are fully encasing the breakerPair.
            (drops all subClusters where the other sibling has the same Pairs (or even more))
            (only keeps nonEmpty clusters that are >=minClusterSize.)
            """
            leftLimit  = breakerPair.index
            rightLimit = breakerPair.index+breakerPair.pairOffset
            resultList=[]
            for cluster in clustersList:
                leftCluster =[pair for pair in cluster if pair.index+pair.pairOffset <rightLimit]
                rightCluster=[pair for pair in cluster if pair.index                 >leftLimit ]

                lefthasUnique=False
                for pair in leftCluster:
                    if pair not in rightCluster:
                        lefthasUnique=True
                        break
                righthasUnique=False
                for pair in rightCluster:
                    if pair not in leftCluster:
                        righthasUnique=True
                        break

                if lefthasUnique:
                    resultList.append(leftCluster)
                if righthasUnique:
                    resultList.append(rightCluster)
                if (not lefthasUnique) and (not righthasUnique):  # (special case, for when the clusters are totally equal)
                    resultList.append(leftCluster)

            resultList = [cluster for cluster in resultList if len(cluster)>=minClusterSize]  # only keep nonEmpty clusters.
            return resultList

        def convert_gapDB_to_LymmPairList(lines_breakingGapDB:list[list[int]])->list[LymmPair]:
            """
            :param: lines_breakingGapDB: a gapDB of one Line, each index contains the gapSizes of that index.
            """
            resultList:list[LymmPair]=[]
            for i in range(len(lines_breakingGapDB)):
                indexes_gapSizeList = lines_breakingGapDB[i]
                for gapSize in indexes_gapSizeList:
                    newPair = LymmPair(i, gapSize)
                    resultList.append(newPair)
            return resultList


        # ----- do the filtering+splitting -----
        resultList = []
        for pattern in PatternsList:
            if pattern.length()==0:
                continue
            if verbose:
                if      ((pattern.messageIDs[0]==5 and pattern.messageIDs[1]==4 and pattern.offset==1) or
                         (pattern.messageIDs[0]==3 and pattern.messageIDs[1]==4 and pattern.offset==6) or
                         (pattern.messageIDs[0]==3 and pattern.messageIDs[1]==5 and pattern.offset==5)):
                    print(f'{Fore.LIGHTBLACK_EX}looking at Pattern: {pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
                    Pattern_scanner.print_Lymm_pattern(cyphertext_whole,
                                                       targetPattern=pattern,
                                                       gapColorDict=gapColorDict,
                                                       onlyPrintmarkedLines=True,
                                                       singlePrint=False)
                    superVerbose=True
                else:
                    superVerbose=False

            PairList = pattern.LymmPairs
            firstMessageID = pattern.messageIDs[0]
            secndMessageID = pattern.messageIDs[1]
            gapDB_A = each_lines_GapDB[firstMessageID]
            gapDB_B = each_lines_GapDB[secndMessageID]
            breakingGapDB = generate_breaking_gapDB(gapDB_A, gapDB_B, pattern.offset)
            breakingGapDB_Lymmed = convert_gapDB_to_LymmPairList(breakingGapDB)

            clustersList = [PairList]  # the initial cluster is just all Pairs together.
            for breakerPair in breakingGapDB_Lymmed:
                clustersList = split_clusters_using_Breakerpair(clustersList, breakerPair)

            if verbose:
                newPatterns:list[LymmPattern]=[]
            for cluster in clustersList:
                cluster = sorted(cluster,key=lambda pair: pair.index)  # sort the list of Lymmpairs, just for visual niceness.
                newPattern=LymmPattern(cluster, pattern.messageIDs, pattern.offset)
                resultList.append(newPattern)
                if verbose:
                    newPatterns.append(newPattern)

            if verbose:
                if superVerbose:
                    print(f"split it into these {len(newPatterns)} unbroken clusters:---------------------------------------------------")
                    for clusterPattern in newPatterns:
                        Pattern_scanner.print_Lymm_pattern(cyphertext_whole,
                                                           targetPattern=clusterPattern,
                                                           gapColorDict=gapColorDict,
                                                           onlyPrintmarkedLines=True,
                                                           singlePrint=False)
                        print("--")

        return resultList
