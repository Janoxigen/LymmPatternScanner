
from colorama import Fore, Back, Style


class LymmPair:
    def __init__(self,index:int,gapsize:int):
                 self.index = index      # (index of the left of the two letters.)
                 self.gapsize = gapsize  # (how many empty spaces are between the two letters.)
                 self.pairOffset  = gapsize+1

    def __str__(self):
        return f"({self.index}:{self.gapsize})"
    def __repr__(self):
        return self.__str__()

class multiLymmPattern:
    def __init__(self,
                 LymmPairs:list[LymmPair],
                 messageDescrs:list[tuple[int,int]],  # for every involved Message we have an (index,offset) Tuple.  (the first offset is always 0)
                 ):
        self.LymmPairs = LymmPairs
        self.messageDescrs = messageDescrs

    def length(self):
        return len(self.LymmPairs)
    def groupSize(self):
        return len(self.messageDescrs)
    def messageCount(self):
        return len(self.messageDescrs)

    def print_pattern(self, cyphertext_whole: str,
                      gapColorDict: dict,
                      onlyPrintmarkedLines=False,
                      alignIsomorphs=False):
        """
        Prints and marks this Lymm-Pattern-nGroup.
        """
        LymmPairList = self.LymmPairs
        lines = cyphertext_whole.split("\n")
        # ---- once for every Line involved in the Isomorph: ----
        for currLineID, currLineOffset in self.messageDescrs:
            # ---- Print the entire Ciphertext with only that Pattern marked: ----
            for lineID in range(0, lines.__len__()):
                currLineStr = lines[lineID]

                hit = lineID == currLineID

                if hit:
                    resultString = self.__mark_one_Lymm_pattern(currLineStr,
                                                                LymmPairList,
                                                                gapColorDict,
                                                                currLineOffset,
                                                                alignIsomorphs)
                    print(resultString)
                elif not hit:
                    if not onlyPrintmarkedLines:
                        print(currLineStr)

    def samePattern(self, otherPattern)->bool:
        """
        Checks if the PATTERNs of the two LymmPatterns are EXACTLY the same, meaning the PLACE doesn't matter, as long as the pattern is the same.
        Does NOT assume that the LymmPair-Lists are sorted, does so itself.
        :returns: TRUE if same Pattern.
        """
        otherPattern:multiLymmPattern
        # --- quick pre-check ---
        if self.length() != otherPattern.length():
            return False

        # --- compare ALL of them ---
        sorted_own = sorted(self.LymmPairs        , key=lambda pair: pair.index)
        sorted_new = sorted(otherPattern.LymmPairs, key=lambda pair: pair.index)
        shift_own = sorted_own[0].index
        shift_new = sorted_new[0].index
        ownPairs_zeroed_tupled = [(pair.index-shift_own,pair.gapsize) for pair in sorted_own]
        newPairs_zeroed_tupled = [(pair.index-shift_new,pair.gapsize) for pair in sorted_new]
        for index in range(self.length()):
            if ownPairs_zeroed_tupled[index] != newPairs_zeroed_tupled[index]:
                return False
        return True

    def __mark_one_Lymm_pattern(self,
                                cypherLine_str: str,
                                LymmPairList:list[LymmPair],
                                gapColorDict:dict,
                                maskOffset:int,
                                alignIsomorphs:bool)->str:
        """
        ATTENTION: This STOPS WORKING properly if you run it twice over a string. That is because the colormarkings themselves are strings.
        :returns: A marked String using colorama-colorcodes
        """
        def mark_letter(listified_string: list, index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Back.RESET

        listified_text = list(cypherLine_str)
        for pair in LymmPairList:  # for each Gap, mark both of its letters in the respective color
            leftLetter_pos = pair.index + maskOffset
            gapSize = pair.gapsize
            rightLetter_pos = leftLetter_pos + pair.pairOffset
            colorcode = gapColorDict[gapSize]
            mark_letter(listified_text, leftLetter_pos, colorcode)
            mark_letter(listified_text, rightLetter_pos, colorcode)
        if alignIsomorphs:
            # we need to cut off the left part if we want to align the Isomorphs.
            listified_text = listified_text[maskOffset:]
        return "".join(listified_text)

    def __str__(self):
        MessageDescrStrings=[f"(msgID={descr[0]},offset={descr[1]})" for descr in self.messageDescrs]
        return f"<LymmPairs:{self.LymmPairs}, {MessageDescrStrings}>"
    def __repr__(self):
        return self.__str__()

class Pattern_scanner:

    @staticmethod
    def find_all_LymmPattern_nGroups(desired_groupsize:int,
                                     cyphertext_whole: str,
                                     gapSizes: list[int],
                                     minimumPatternSize=2,
                                     verbose=False)->list[multiLymmPattern]:
        """
        Finds all the n-sized Groups of repeating LymmPatterns.
        :param: gapSizes: a list of the Sizes that we want to check.
        """
        if desired_groupsize<2:
            raise Exception("groupsize of LymmPatternGroups must be at least 2.")
        if minimumPatternSize<2:
            raise Exception("PatternSize of LymmPatterns must be at least 2.")
        # -----------------------
        # ----- PREPARATION -----
        # -----------------------
        cipherLines = cyphertext_whole.split("\n")
        each_lines_GapDB = []  # this will be one entry for each Line-ID, ergo an entry is a list, mapping  position->Gaps
        for lineID in range(0, cipherLines.__len__()):
            currLine = cipherLines[lineID]
            currDB = Pattern_scanner.__gather_gapDB_of_line(currLine, gapSizes)
            each_lines_GapDB.append(currDB)

        allPatternsList = []

        # ---------------------------------------
        # ----- Help-classes and functions -----
        # ---------------------------------------
        class primordialNGroup:
            """
            This class is used to store the currently gathered Pattern, aswell as the involved Messages and offsets.
            """
            def __init__(self,
                         remainingGaps_DB: list[list[int]],
                         messageDescrs: list[tuple[int, int]]):
                self.remainingGaps_DB = remainingGaps_DB
                self.messageDescrs = messageDescrs

        def overlay_GapDBs(gapDB_A: list[list[int]],
                           gapDB_B: list[list[int]]
                           )      ->list[list[int]]:
            """
            returns a new GapDB, containing only the gaps that BOTH DBs contained.
            """
            resulting_gapDB = []
            comparelength = min(gapDB_A.__len__(), gapDB_B.__len__())
            for index in range(0,comparelength):
                new_GapList = [gapSize for gapSize in gapDB_A[index] if gapSize in gapDB_B[index]]
                resulting_gapDB.append(new_GapList)
            return resulting_gapDB

        def count_pairs_in_GapDB(gapDB: list[list[int]])->int:
            sum = 0
            for currLetters_GapSizeList in gapDB:
                sum += len(currLetters_GapSizeList)
            return sum

        def LymmPairify_GapDB(gapDB: list[list[int]])->list[LymmPair]:
            resultList = []
            for index in range(0, len(gapDB)):
                currLetters_GapSizeList = gapDB[index]
                for gapSize in currLetters_GapSizeList:
                    newLymmPair = LymmPair(index, gapsize=gapSize)
                    resultList.append(newLymmPair)
            return resultList

        # --------------------------------
        # ------- SCANNING-function ------
        # --------------------------------
        def faLPnG_recursion(kickstarterRecursion=True,
                             oldGroupSize:int=None,
                             previous_scanLineID:int=None,
                             previous_startOffset:int=None,
                             mainLineID:int=None,
                             currently_worked_group:primordialNGroup=None):
            """
            This function goes over (the rest of) the unchecked other messages/offsets.
            If it finds another offset where the overlapping Pattern isn't empty, it goes one
            recursion deeper, unless the desiredGroupSize is already reached.
            All found Patterns are put into the allPatternsList.
            """
            if kickstarterRecursion:
                for mainLineID in range(0, cipherLines.__len__()):
                    initial_gapDB = each_lines_GapDB[mainLineID]
                    initial_messageDescrs = [(mainLineID, 0)]
                    newNgroup = primordialNGroup(remainingGaps_DB=initial_gapDB,
                                                 messageDescrs=initial_messageDescrs)
                    faLPnG_recursion(kickstarterRecursion=False,
                                     oldGroupSize=1,
                                     previous_scanLineID=0,
                                     previous_startOffset=None,  # I had to do this is such a stupid way because otherwise i would sometimes pass a self-comparing startOffset.
                                     mainLineID=mainLineID,
                                     currently_worked_group=newNgroup)
                return
            # ---- if not KickstarterRecursion: ----
            newGroupSize = oldGroupSize +1
            current_remaining_GapDB = currently_worked_group.remainingGaps_DB
            firstIteration=True
            for scanLineID in range(previous_scanLineID, cipherLines.__len__()):
                maxOffset = cipherLines[mainLineID].__len__()
                secondLines_gapDB = each_lines_GapDB[scanLineID]

                startoffset = 0  # the offset can only be positive, but by swapping the roles of main- and secondLine, we do an "inverted" test.
                if scanLineID <= mainLineID:
                    """
                    if we are comparing it to the line itself, we can only scan whatever
                    is to the "right" of what was already scanned. (to prevent self-finds.)

                    This is also a startoffset-adjustment to prevent duplicate finds of zero-offsets between different messages.
                    """
                    startoffset = 1  # (ergo we don't start at 0-Offset)

                if firstIteration:
                    if previous_startOffset is not None:
                        startoffset=previous_startOffset
                    # Note: if it is None, then this is the recursion directly under the kickstarterRecursion,
                    #   which means that we can choose the initial_startOffset on our own.

                for currOffset in range(startoffset, maxOffset):
                    if firstIteration:
                        firstIteration = False
                        continue  # we need to skip this iteration because it is the one from which we were called.

                    offsetted_gapDB = secondLines_gapDB[currOffset:]  # we slice off every gap before the offset-index.
                    overlapped_GapDB = overlay_GapDBs(current_remaining_GapDB, offsetted_gapDB)
                    pairCount = count_pairs_in_GapDB(overlapped_GapDB)
                    if pairCount <minimumPatternSize:
                        continue  # skip all patterns with not enough LymmPairs.

                    newMessageDescrs = currently_worked_group.messageDescrs + [(scanLineID,currOffset)]
                    # ---- if group NOT finished, recurse: ----
                    if newGroupSize <desired_groupsize:
                        newNgroup = primordialNGroup(remainingGaps_DB=overlapped_GapDB, messageDescrs=newMessageDescrs)
                        faLPnG_recursion(kickstarterRecursion=False,
                                         oldGroupSize=newGroupSize,
                                         previous_scanLineID=scanLineID,
                                         previous_startOffset=currOffset,
                                         mainLineID=mainLineID,
                                         currently_worked_group=newNgroup)
                    # ---- if group YES finished, Lymmify it and store it as a success: ----
                    else:
                        pattern = LymmPairify_GapDB(overlapped_GapDB)
                        newLymmPattern = multiLymmPattern(pattern, messageDescrs=newMessageDescrs)
                        allPatternsList.append(newLymmPattern)

        # --------------------------------
        # --------- RECURSION-call -------
        # --------------------------------
        faLPnG_recursion(kickstarterRecursion=True)
        if verbose:
            print(f"found a total of {len(allPatternsList)} nGroups of matching Lymm Patterns.")
        return allPatternsList

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
        Goes over the provided String and adds coloring to all the characters that are in a Gap
        in the provided gapDB.
        UNUSED as of now, but might be usefull someday to mark Isomorphs when you only have gapDBs at your disposition.
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
                                               PatternsList:list[multiLymmPattern],
                                               minClusterSize=2,
                                               gapColorDict: dict=None,
                                               verbose=False
                                               )->list[multiLymmPattern]:
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

        def generate_breaking_gapDB(messageDescrs: list[tuple[int,int]],
                                    each_lines_GapDB: list[list[list[int]]]
                                    )->list[list[int]]:
            """
            Returns a list of lists.
            For every position (accounting for offset), a list of all the gaps that aren't in ALL gapDBs at that position.
            (Assumes that the offset is possible with those gapDBs)
            Note: The resulting list is as big as the offsets and DBsizes allow.

            :param: messageDescrs: for every involved Message we have an (index,offset) Tuple.  (the first offset is always 0)
            :param: each_lines_GapDB: For every line one List that is: For every Letter a List of Gapsizes at that Index.
            """
            resultDB = []
            # ---- fetch all the gapDBs ----
            allGapDBs = []
            for lineID,offset in messageDescrs:
                offsetted_gapDB = each_lines_GapDB[lineID][offset:]
                allGapDBs.append(offsetted_gapDB)
            allGapDBsizes = [len(DB) for DB in allGapDBs]
            # ---- find all the breakingGaps of each index----
            maxScanIndex = min(allGapDBsizes)
            for scanIndex in range(maxScanIndex):
                allBreakersDB_ofthisIndex = set() #using set for easy duplicatePrevention.
                for mainDB_ID, mainGapDB in enumerate(allGapDBs):
                    mainGapSizeList = mainGapDB[scanIndex]
                    for secndDB_ID, secndGapDB in enumerate(allGapDBs):
                        if secndDB_ID != mainDB_ID:
                            secndGapSizeList = secndGapDB[scanIndex]
                            newFoundBreakers = [gapSize for gapSize in mainGapSizeList if gapSize not in secndGapSizeList]
                            allBreakersDB_ofthisIndex.update(newFoundBreakers)  # add all newFoundBreakers to the allBreakers.
                resultDB.append(list(allBreakersDB_ofthisIndex))

            return resultDB

        def split_clusters_using_Breakerpair(clustersList:list[list[LymmPair]], breakerPair: LymmPair)->list[list[LymmPair]]:
            """
            For every cluster, this creates a "left" and "right" side cluster based on the breakerPair.
            Btw, this (as a sideffect) filters out all LymmPairs that are fully encasing the breakerPair.
            (drops all subClusters that are already fully contained within another cluster.)
            (only keeps nonEmpty clusters that are >=minClusterSize.)
            """
            leftLimit  = breakerPair.index
            rightLimit = breakerPair.index+breakerPair.pairOffset
            splittedClusters_List=[]
            # ---- split every cluster: ----
            for cluster in clustersList:
                leftCluster =[pair for pair in cluster if pair.index+pair.pairOffset <rightLimit]
                rightCluster=[pair for pair in cluster if pair.index                 >leftLimit ]
                if len(leftCluster)  >=minClusterSize: splittedClusters_List.append(leftCluster)
                if len(rightCluster) >=minClusterSize: splittedClusters_List.append(rightCluster)

            # ---- only keep clusters that are not fully contained within another cluster: ----
            resultList=[]
            for AnkerCluster in splittedClusters_List:

                ankerIsUnique=True
                for currCluster in resultList:
                    foundUnique=False
                    for pair in AnkerCluster:
                        if pair not in currCluster:
                            foundUnique=True
                            break
                    if not foundUnique:
                        ankerIsUnique=False
                        break

                if ankerIsUnique:
                    newResultList = []
                    newResultList.append(AnkerCluster)
                    for currCluster in resultList:
                        currIsUnique = False
                        for pair in currCluster:
                            if pair not in AnkerCluster:
                                currIsUnique = True
                                break
                        if currIsUnique:
                            newResultList.append(currCluster)
                    resultList=newResultList
            return resultList

        def convert_gapDB_to_LymmPairList(gapDB:list[list[int]])->list[LymmPair]:
            """
            Note: The resulting
            :param: lines_breakingGapDB: a gapDB of one Line, each index contains the gapSizes of that index.
            """
            resultList:list[LymmPair]=[]
            for i in range(len(gapDB)):
                indexes_gapSizeList = gapDB[i]
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
                print(f'{Fore.LIGHTBLACK_EX}looking at Pattern: {pattern}  GAPCOUNT:{pattern.length()}{Fore.RESET}')
                pattern.print_pattern(cyphertext_whole, gapColorDict, onlyPrintmarkedLines=True, alignIsomorphs=False)

            PairList = pattern.LymmPairs
            breakingGapDB = generate_breaking_gapDB(messageDescrs=pattern.messageDescrs, each_lines_GapDB=each_lines_GapDB)
            breakingGapDB_Lymmed = convert_gapDB_to_LymmPairList(breakingGapDB)

            clustersList = [PairList]  # the initial cluster is just all Pairs together.
            for breakerPair in breakingGapDB_Lymmed:
                clustersList = split_clusters_using_Breakerpair(clustersList, breakerPair)

            if verbose:
                newPatterns:list[multiLymmPattern]=[]
            for cluster in clustersList:
                cluster = sorted(cluster,key=lambda pair: pair.index)  # sort the list of Lymmpairs, just for visual niceness.
                newPattern=multiLymmPattern(LymmPairs=cluster, messageDescrs=pattern.messageDescrs)
                resultList.append(newPattern)
                if verbose:
                    newPatterns.append(newPattern)

            if verbose:
                print(f"split it into these {len(newPatterns)} unbroken clusters:---------------------------------------------------")
                for clusterPattern in newPatterns:
                    clusterPattern.print_pattern(cyphertext_whole,gapColorDict,onlyPrintmarkedLines=True,alignIsomorphs=False)
                    print("--")

        return resultList
