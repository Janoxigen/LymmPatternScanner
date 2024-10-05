
from colorama import Fore, Back, Style
from SETTINGS import *
from internal_tools import *


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
                      alignIsomorphs=False,
                      allIntoOneCiphertext=False,
                      onlyPrintThisMessageID=None):
        """
        Prints and marks this Lymm-Pattern-nGroup.
        These two Flags DO NOT WORK if [allIntoOneCiphertext] is enabled:
            onlyPrintmarkedLines
            alignIsomorphs

        :param: allIntoOneCiphertext: (takes priority over aligning and single-line-printing) if TRUE, it will print all Patterns into one single ciphertext, potentially overlapping.
        :param: alignIsomorphs: if TRUE, all patterns are perfectly below each other, but [allIntoOneCiphertext] takes priority and removes this flag.
        :param: onlyPrintmarkedLines: if TRUE, it only prints the line of the pattern for each pattern. but [allIntoOneCiphertext] takes priority and removes this flag.
        :param: onlyPrintThisMessageID: if NONE, it will print regularily, but if an INT is supplied, only that MessageDescr will be printed
        """
        LymmPairList = self.LymmPairs
        lines = cyphertext_whole.split("\n")
        if onlyPrintThisMessageID is not None:
            allIntoOneCiphertext=False
        if not allIntoOneCiphertext:
            if onlyPrintThisMessageID is not None:
                chosenMessageDescrs=[self.messageDescrs[onlyPrintThisMessageID]]
            else:
                chosenMessageDescrs=self.messageDescrs
            # ---- once for every Line involved in the Isomorph: ----
            for currLineID, currLineOffset in chosenMessageDescrs:
                # ---- Print the entire Ciphertext with only that Pattern marked: ----
                for lineID in range(0, lines.__len__()):
                    currLineStr = lines[lineID]
                    if lineID==currLineID:
                        resultString = self.__mark_one_Lymm_pattern(currLineStr,
                                                                    LymmPairList,
                                                                    gapColorDict,
                                                                    currLineOffset,
                                                                    alignIsomorphs)
                        output(resultString)
                    else:
                        if not onlyPrintmarkedLines:
                            output(currLineStr)
        if allIntoOneCiphertext:
            for lineID in range(0, lines.__len__()):
                listified = list(lines[lineID])
                for currLineID, currLineOffset in self.messageDescrs:
                    if lineID==currLineID:
                        self.__mark_one_Lymm_pattern_listified(listified, self.LymmPairs, gapColorDict, currLineOffset)
                output("".join(listified))

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
                                LymmPairList: list[LymmPair],
                                gapColorDict: dict,
                                maskOffset: int,
                                alignIsomorphs: bool) -> str:
        """
        ATTENTION: This STOPS WORKING properly if you run it twice over a string. That is because the colormarkings themselves are strings.
        :returns: A marked String using colorama-colorcodes
        """

        def mark_letter(listified_string: list[str], index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Style.RESET_ALL

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

    @staticmethod
    def create_LymmPattern_from_structureString(structureString:str,
                                                position_within_mainline: int,
                                                messageDescrs:list[tuple[int,int]],
                                                spacingLetter="-"):
        """
        structureString looks like this:  A---BBAB--C--C
        "-" is the spacingLetter.

        Returns a multiLymmPattern that follows the provided description.
        Note: since the offsets in the messageDescrs can only ever be positive, you need to use the leftmost LymmPattern as the mainLine.

        Note: DO NOT USE THIS SELFMADE PATTERN for further computations using find_all_LymmPattern_nGroups()!
        That is because that function exploits some naturally occurring properties of the multiLymmPattern-instances that it creates.
        """
        for pair in messageDescrs:
            if pair[1]<0:
                raise Exception("offsets in MessageDescrs can never be negative, they must be positive, and relative to the leftmost LymmPattern.")
        # ---- parse the structureString into a LymmPair-List ----
        pairList: list[LymmPair]=[]
        for ID_A, lettr_A in enumerate(structureString):
            if lettr_A==spacingLetter:
                continue
            for ID_B, lettr_B in enumerate(structureString):
                if lettr_B==spacingLetter:
                    continue
                if ID_B > ID_A:
                    if lettr_A==lettr_B:
                        newPair = LymmPair(index=ID_A+position_within_mainline, gapsize=ID_B-ID_A-1)
                        pairList.append(newPair)
        # ---- create a new multiLymmPattern ----
        return multiLymmPattern(pairList,messageDescrs)

    def __mark_one_Lymm_pattern_listified(self,
                                          listified_text: list[str],
                                          LymmPairList:list[LymmPair],
                                          gapColorDict:dict,
                                          maskOffset:int):
        """
        MODIFIES the listified_text by adding colorama-colorcodes to the marked indexes.
        This is useful because it allows multiple marking-passes over the same ciphertextLine, as long as
        you didn't convert it back to a string yet.
        """
        def mark_letter(listified_string: list[str], index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Style.RESET_ALL

        for pair in LymmPairList:  # for each Gap, mark both of its letters in the respective color
            leftLetter_pos = pair.index + maskOffset
            gapSize = pair.gapsize
            rightLetter_pos = leftLetter_pos + pair.pairOffset
            colorcode = gapColorDict[gapSize]
            mark_letter(listified_text, leftLetter_pos, colorcode)
            mark_letter(listified_text, rightLetter_pos, colorcode)

    def __str__(self):
        MessageDescrStrings=[f"(msgID={descr[0]},offset={descr[1]})" for descr in self.messageDescrs]
        return f"<LymmPairs:{self.LymmPairs}, {MessageDescrStrings}>"
    def __repr__(self):
        return self.__str__()

class stringPattern:
    """
    A different Notation of LymmPatterns, based on a representative-string.

    1: The [representative-string] defines the EXACT repetitions and pattern-length.
    2: The [occurances] defines where this exact pattern occurs (messageID+position).
    """
    def __init__(self, reprString:str, occurances:set[tuple[int,int]]):
        """
        :param occurances: for every occurance we have a (MessageID,position) Tuple.  (position referrs to the index of the patterns first letter.)
        """
        self.reprStr = reprString
        self.occurances = occurances

    def print_pattern(self, cyphertext_whole: str):
        """
        For every occurrance, it prints the Line where it occurred in redFont, while the actual segment is
        in regular font, with gaps colored.
        It doesn't actually verify wether those patterns are actually in the text, it just colors it naively.
        If ALIGN_ISOMORPHS=True in SETTINGS.py, it will align the isomorphs to the leftmost one.
        The setting PRINT_ONE_CIPHERTEXT_PER_LYMMGROUP doesn't work here, because i haven't implemented it (yet).
        """
        cipherLines = cyphertext_whole.split("\n")
        patLen = self.reprStr.__len__()
        colorMask = self.__generate_colorMask(self.reprStr)
        if ALIGN_ISOMORPHS is True:
            ankerPos=min([pos for mesgID,pos in self.occurances])
        for mesgID,pos in self.occurances:
            line = cipherLines[mesgID]
            posBackup=pos
            if ALIGN_ISOMORPHS is True:
                shift=pos-ankerPos
                line=line[shift:]  # left-truncate Line by shiftamount
                pos =pos-shift  # left-shift patternPos by shiftamount
            end = pos + patLen
            preSegment = line[:pos]
            segmentStr = line[pos:end]
            endSegment = line[end:]
            coloredSegment = self.__apply_colorMask(segmentStr, colorMask)
            stitched = f"{Fore.RED}{preSegment}{Fore.RESET}{coloredSegment}{Fore.RED}{endSegment}{Fore.LIGHTBLACK_EX}   {mesgID},{posBackup}"
            output(stitched)

    def fetch_randomOcc(self)->tuple[int,int]:
        """
        Returns NONE if pattern has zero Occs.
        (This scuffed thing is needed because python HAS NO DEFAULT WAY OF POPPING A RANDOM SET ELEMENT!!! REEEEE)
        """
        for elem in self.occurances:
            return elem

    @staticmethod
    def __generate_colorMask(s: str) -> list[str]:
        """
        Generates a list of ColorCodes, one for each Index.
        These ColorCodes will mark gap-positions.
        Needs GAPCOLORS to be defined in SETTINGS.py
        :returns fills an index with ColorCode if colored, NONE overwise.
        """
        stringLen =len(s)
        result :list[str] =[None]*stringLen  # ignore typewarning.
        lastSeenPosDict :dict[str,int] =dict()
        for pos,letr in enumerate(s):
            if letr not in lastSeenPosDict.keys():
                lastSeenPosDict[letr] = pos
            else:
                # -- colorize both indexes --
                prev = lastSeenPosDict[letr]
                gapSize = pos -prev -1  # (gapsize 0="AA"  1="A-A"  2="A--A"  3="A---A")
                if gapSize in GAPCOLORS.keys():
                    color = GAPCOLORS[gapSize]
                    result[pos] = color
                    result[prev] = color
                # -- reset lastSeen-pos --
                lastSeenPosDict[letr] = pos
        return result

    @staticmethod
    def __apply_colorMask(s: str, colMask: list[str]) -> str:
        """
        Applies a given ColorMask to a given String.
        Throws exception if colormask is too short for string.
        Can only be applied once because it messes up the lettercount/position of the given string after coloring.
        """
        result = ""
        for pos,letr in enumerate(s):
            color = colMask[pos]
            if color is None:
                result +=letr
            else:
                result += color +letr+ Style.RESET_ALL
        return result


class Pattern_scanner:

    @staticmethod
    def find_all_LymmPattern_nGroups(desired_groupsize:int,
                                     cyphertext_whole: str,
                                     gapSizes: list[int],
                                     minimumPatternSize=2,
                                     previous_LymmPatterns:list[multiLymmPattern]=None,
                                     verbose=False)->list[multiLymmPattern]:
        """
        Finds all the n-sized Groups of repeating LymmPatterns.
        :param: gapSizes: a list of the Sizes that we want to check, all other ones are ignored.
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
                        if previous_startOffset is not None:
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

        def alternative_kickstarter(seedPattern: multiLymmPattern):
            """
            The user can supply an already computed multiLymmPattern and this function will continue the
            recursion-search by figuring what the state was when the given LymmPattern was found.
            """
            # --- deduce the state when the seedPattern was found. ---
            mainLineID      = seedPattern.messageDescrs[0][0]   # the first Tuple is for the mainLine, so we take the first digit of that Tuple for the ID.
            last_scanLineID = seedPattern.messageDescrs[-1][0]  # the last Tuple is for the line where the seedPattern was found.
            last_Offset     = seedPattern.messageDescrs[-1][1]  # the last Tuple is for the line where the seedPattern was found.
            patternSize = seedPattern.groupSize()

            # --- recreate the gapDB ---
            # Explanation:
            #  Since the given seedPattern is the result of what remains after a "dividing into unbroken
            #  clusters...", we can be sure that the only gaps that exist within pattern-bounds (and therefore
            #  are relevant to the Pattern) are the ones in the pattern themselves.
            mainLineLength = len(cipherLines[mainLineID])
            recreated_gapDB: list[list[int]]= []
            for _ in range(mainLineLength):
                recreated_gapDB.append([])
            for pair in seedPattern.LymmPairs:
                recreated_gapDB[pair.index].append(pair.gapsize)

            # --- kickstart the recursion. ---
            newNgroup = primordialNGroup(remainingGaps_DB=recreated_gapDB,
                                         messageDescrs=seedPattern.messageDescrs)
            faLPnG_recursion(kickstarterRecursion=False,
                             oldGroupSize=patternSize,
                             previous_scanLineID=last_scanLineID,
                             previous_startOffset=last_Offset,
                             mainLineID=mainLineID,
                             currently_worked_group=newNgroup)


        # --------------------------------
        # --------- RECURSION-call -------
        # --------------------------------
        if previous_LymmPatterns is None:
            faLPnG_recursion(kickstarterRecursion=True)
        elif previous_LymmPatterns is not None:
            for currSeed in previous_LymmPatterns:
                alternative_kickstarter(currSeed)

        if verbose:
            print(f"found a total of {len(allPatternsList)} nGroups of matching Lymm Patterns.")
        return allPatternsList

    # Done, seems to work
    @staticmethod
    def crossBreeding_LymmPatternScanner(cyphertext_whole: str, verbose=False):
        """
        TOTALLY Reworked Algorithm.
        Is MUCH faster now.
        It works by "breeding" pairs of already found LymmPatternGroups, to extract any and all existing
        subPatterns that are in both Groups.
        In order to pull that off, I switched to a totally different notation of LymmPatterns: string-representatives.
        Those string-representatives have the additional benefit of specifying the exact range of the pattern, not just
        the involved gaps.

        Note: filters groupsize using MINIMUM_GROUPSIZE and Patterns using MINIMUM_PATTERN_SIZE from SETTINGS.py
        """
        # -----------------------
        # ----- PREPARATION -----
        # -----------------------
        cipherLines = cyphertext_whole.split("\n")

        # ---------------------------------------
        # ----- Help-classes and functions -----
        # ---------------------------------------
        # Done, seems to work
        def isBoring(s:str) -> bool:
            """
            :returns: TRUE if the given string doesn't have at least MINIMUM_PATTERN_SIZE many LymmPairs.
            """
            letterCounts: dict[str, int] = dict()
            for letr in s:
                if letr not in letterCounts.keys():
                    letterCounts[letr] =0
                letterCounts[letr] +=1
            pairCount = 0
            for letr in letterCounts.keys():
                # (we do this weird calculation because each letter causes pairs with ALL future repetitions of said letter.)
                n = letterCounts[letr] - 1
                cumulative = (n*(n+1)) //2
                pairCount += cumulative
            if pairCount < MINIMUM_PATTERN_SIZE: return True  # is boring
            return False  # is NOT boring

        # Done, seems to work
        def breakerPair_splitter(strA:str,
                                 strB:str
                                 ) -> list[tuple[str, int]]:
            """
            Finds all the unbroken segments when overlapping the two strings.
            Does NOT shift the inputs, has to be done by the caller.
            Automatically drops any "boring" patterns (smaller than MINIMUM_PATTERN_SIZE).

            :returns: one Tuple per unbroken segment, with an integer that tells the index where the segment starts.
            """
            foundSegDescrs :list[tuple[str,int]] = []

            overlapLen = min(len(strA), len(strB))
            currSegStart = 0

            lastPosDict_A :dict[str,int] =dict()  # tells at which position this A-char was seen.
            lastPosDict_B :dict[str,int] =dict()  # tells at which position this B-char was seen.
            seenAs :set[str] = set()
            seenBs :set[str] = set()

            ##print(strA + "ä")  # TESTPRNT
            ##print(strB + "ä")  # TESTPRNT

            for currPos in range(0, overlapLen):
                ##currSegStr = strA[currSegStart: currPos + 1]  # for TESTPRNT  # a "-1" isn't needed for currPos cuz the string-slicing already cuts off one too many from the right.
                ##buffer = "".join(["."] * (currSegStart))  # for TESTPRNT
                ##print("")  # linebreak previous line  # TESTPRNT
                ##print(buffer + currSegStr, end="")  # for TESTPRNT
                ##print(f"     [{currSegStart}:{currPos}+1]", end="")  # for TESTPRNT
                letrA = strA[currPos]
                letrB = strB[currPos]
                if letrA not in seenAs:
                    seenAs.add(letrA)
                    lastPosDict_A[letrA] =-1  # temporary value. =-1 because it needs to not overpower breakerPairs.
                if letrB not in seenBs:
                    seenBs.add(letrB)
                    lastPosDict_B[letrB] =-1  # temporary value. =-1 because it needs to not overpower breakerPairs.
                # -- do breakage-check --
                lastPos_A = lastPosDict_A[letrA]
                lastPos_B = lastPosDict_B[letrB]
                if lastPos_A != lastPos_B:
                    # ergo: breakage detected!
                    # -- check if is currSeg affected: --
                    earliestBreakPoint = max(lastPos_A, lastPos_B)
                    if currSegStart <= earliestBreakPoint:
                        ##print(f"   found breakage! ({letrA}@{lastPos_A} vs {letrB}@{lastPos_B})", end="")  # TESTPRNT
                        # -- save segment if it isn't boring --
                        oldSegStr = strA[currSegStart: currPos]  # a "-1" isn't needed for currPos cuz the string-slicing already cuts off one too many from the right.
                        if not isBoring(oldSegStr):
                            ##print(f"   valid Combi: ö{oldSegStr}ö", end="")  # TESTPRNT
                            foundSegDescrs.append((oldSegStr, currSegStart))
                        # -- update segStart --
                        currSegStart = max(lastPos_A+1, lastPos_B+1)  # move new segStart to AFTER the latest breakPoint.
                lastPosDict_A[letrA] = currPos
                lastPosDict_B[letrB] = currPos
                # -- the final iteration needs to be a completed segment too: --
                if currPos == overlapLen-1:
                    # if we reached the last letter, we force the current Segment to finish:
                    segStr = strA[currSegStart:overlapLen]
                    if not isBoring(segStr):
                        ##print("   final is valid Combi!", end="")  # TESTPRNT
                        foundSegDescrs.append((segStr, currSegStart))
            ##print("ö")  # linebreak previous line  # TESTPRNT
            return foundSegDescrs

        # Done, should work
        def samePattern(strA:str, strB:str) -> bool:
            """
            :returns: TRUE if given reprStrings that have exactly the same LymmPattern.
            """
            if len(strA) != len(strB): return False
            mappingDict: dict[str,str] = dict()  # this will map the substitution from strA to strB.
            seenAs: set[str] = set()
            seenBs: set[str] = set()
            # -- check if strA can be substituted into strB: --
            for pos, letrA in enumerate(strA):
                letrB = strB[pos]
                if (letrA in seenAs) and (letrB in seenBs):
                    if mappingDict[letrA] != letrB:
                        return False  # if letterA was previously matched with another B.
                elif (letrA not in seenAs) and (letrB not in seenBs):
                    mappingDict[letrA] = letrB
                    seenAs.add(letrA)
                    seenBs.add(letrB)
                else:  # if only one of them was seen
                    return False
            return True  # only reaches here if no mismatch was found.

        # Done, seems to work
        def is_subPattern(subPat: stringPattern, parent: stringPattern, verbose=False)->bool:
            """
            :returns: TRUE, if subPat is a physical subPattern of parent.

            "physical" subPattern means that EVERY segment from subPat must be fully contained in a segment from
            parent, at EXACTLY the same place.

            To detect that, we need to find said "exact place" by using one subPat-segment as an example.
            And then, all the other subPat-segment need to be checked for existance of parent-segments that overlap
            them with that exact placement.
            Note: The initial example-search might find multiple candidates for "exact places", so each of them needs
            to be tested. Only if ALL candidates are ruled out does the result "not subPattern" say TRUE.

            Note: There is also the early-abort in case that subPatt has larger segments thatn parent does.

            Might raise Exception if the subPattern has no occurances.
            """
            subLen=len(subPat.reprStr)
            parLen=len(parent.reprStr)
            if subLen>parLen:
                return False

            if verbose:
                print("subChecking:")
                subPat.print_pattern(cyphertext_whole)
                print("versus")
                parent.print_pattern(cyphertext_whole)

            # --- find every candidate for exactPlaces ---
            maxOffset=parLen-subLen
            testID,testPos =subPat.fetch_randomOcc()
            for otherID,otherPos in parent.occurances:
                if testID ==otherID:  # must be in same message.
                    if testPos >=otherPos:  # must not be too far left.
                        if testPos <=otherPos+maxOffset:  # must not be too far right.
                            # CONTAINED!
                            exactOffset= testPos-otherPos
                            if verbose:
                                print(f"found exPosCandidate:  {testPos}={otherPos}+{exactOffset}")
                            # --- scan all other Occs from subPat: ---
                            contained=True
                            for subID,subPos in subPat.occurances:
                                # -- verify that there exists a parentOcc that contains this subOcc at the EXACT position. --
                                found=False
                                for parID,parPos in parent.occurances:
                                    if subID ==parID:
                                        if subPos==parPos+exactOffset:
                                            if verbose:
                                                print(f"{subID},{subPos} is in {parID},{parPos}+{exactOffset}")
                                            found=True
                                            break
                                if found is False:
                                    contained=False
                                    break  # break this exactOffset-scan if even one subOcc isn't contained anywhere.
                            if contained is True:
                                if verbose:
                                    print(f"subpat indeed!  for exPos={exactOffset}")
                                return True
            #(at this point, we scanned all exactPlace-candidates and none of them managed to contain ALL occs of subPat.)
            return False

        # --------------------------------
        # ------- Breeding-function ------
        # --------------------------------
        # Done, seems to work
        def breed(patA: stringPattern, patB: stringPattern) -> list[stringPattern]:
            """
            Finds all the non-broken sub-Patterns that occur in both Patterns, filters out
            low-complexity patterns and creates new stringPattern-Instances to describe the results.
            Also: Checks all found sub-Patterns for bigger groups: maybe two subPatterns are actually one big group?
            """
            foundPatterns: list[stringPattern] = []
            lenA = len(patA.reprStr)
            lenB = len(patB.reprStr)
            Aoccs = patA.occurances
            Boccs = patB.occurances
            maxLeftShiftA = max(0, lenA-2)  # the -2 is such that there is at least 2 overlapping letters when only A is shifted to the left.
            maxLeftShiftB = max(0, lenB-2)  # the -2 is such that there is at least 2 overlapping letters when only B is shifted to the left.
            shiftrange = range(-1*maxLeftShiftA, maxLeftShiftB+1)  # the +1 because range() cuts off the rightmost value by one.
            # -- for every relative offset --
            for currShift in shiftrange:
                # if SHIFT is negative, strA will be shifted left, if SHIFT is positive, strB will be shifted left.
                # SHIFT=0 means none of them are edited.
                # "shifted left" means cutting off the lefthand side by SHIFT-many letters.
                if currShift <0:
                    shiftA = -1*currShift
                    shiftB = 0
                elif currShift >0:
                    shiftA = 0
                    shiftB = currShift
                else:
                    shiftA = 0
                    shiftB = 0
                strA = patA.reprStr[shiftA:]
                strB = patB.reprStr[shiftB:]
                # -- do breakerpair-splitting --
                segmentDescrs: list[tuple[str,int]] = breakerPair_splitter(strA, strB)
                # -- convert found segments to stringPatterns -- (has to calculate the occurance-positions.)
                newPatterns: list[stringPattern] = []
                for currSeg, offset in segmentDescrs:
                    offsettedOccs_A = [(mesgID, pos+offset+shiftA) for mesgID,pos in Aoccs]
                    offsettedOccs_B = [(mesgID, pos+offset+shiftB) for mesgID,pos in Boccs]
                    occs = offsettedOccs_A + offsettedOccs_B
                    newPattern = stringPattern(reprString=currSeg, occurances=set(occs) )
                    newPatterns.append(newPattern)
                # -- check for segments that are actually one bigger group. --
                for currPat in newPatterns:
                    matched = False
                    for oldPat in foundPatterns:
                        if samePattern(currPat.reprStr, oldPat.reprStr):
                            nonOverlap=[occ for occ in currPat.occurances if occ not in oldPat.occurances]
                            oldPat.occurances.update(nonOverlap)  # add any nonOverlap to the oldPats Occs.
                            matched = True
                            break
                    if matched is False:
                        foundPatterns.append(currPat)
                # (at this point, all of this currShifts newPatterns have properly been ingested into foundPatterns.)
            # (at this point, all shifts have been computed.)
            return foundPatterns

        # -----------------------------------------------------
        # --------- MAIN ALGORITHM: Systematic breeding -------
        # -----------------------------------------------------
        # -- go over all "primal-ancestor-patterns" --
        gatheredPatterns: list[stringPattern] = []
        for lineID, lineStr in enumerate(cipherLines):
            if verbose:
                output(f"mainlineID:{lineID},   {lineStr}")
            startOccs={(lineID, 0)}  # this scuffed notation creates a set with the Tuple (lineID,0).
            primalPatt = stringPattern(reprString=lineStr, occurances=startOccs)
            gatheredPatterns.append(primalPatt)
            # ---- do systematic breeding until T0D0list is empty. ----
            newFoundPatterns: list[stringPattern] = []
            for otherPatt in gatheredPatterns:
                newFamily = breed(primalPatt, otherPatt)
                newFoundPatterns.extend(newFamily)
            # (at this point, we bred this primalPatt with every single pattern from [gatheredPatterns], the results landing in [newFoundPatterns])
            # --- remove any subPattern between [newFoundPatterns] and [gatheredPatterns] ---
            for newPatt in newFoundPatterns.copy():
                nextGatherList: list[stringPattern] = []
                # -- check if newPatt is SAMEPATTERN of another pattern in the same generation:-- (merge A into B if yes.)
                isSamePattern = False
                for otherNewPat in newFoundPatterns:
                    if newPatt != otherNewPat:
                        if samePattern(newPatt.reprStr, otherNewPat.reprStr):
                            # -- if samePattern, insert A's occs into B --
                            isSamePattern = True
                            nonOverlap = [occ for occ in newPatt.occurances if occ not in otherNewPat.occurances]
                            otherNewPat.occurances.update(nonOverlap)  # add any nonOverlap to the oldPats Occs.
                            break
                if isSamePattern is True:
                    newFoundPatterns.remove(newPatt)
                    continue  # end this newPatts iteration
                # -- check if newPatt is SAMEPATTERN of another pattern in [gatheredPatterns]:-- (merge A into B if yes.)
                isSamePattern = False
                for oldPat in gatheredPatterns:
                    if newPatt != oldPat:
                        if samePattern(newPatt.reprStr, oldPat.reprStr):
                            # -- if samePattern, insert A's occs into B --
                            isSamePattern = True
                            nonOverlap = [occ for occ in newPatt.occurances if occ not in oldPat.occurances]
                            oldPat.occurances.update(nonOverlap)  # add any nonOverlap to the oldPats Occs.
                            break
                if isSamePattern is True:
                    continue  # end this newPatts iteration
                # -- check if newPatt is subPat of another pattern in the same generation:--
                isSubPattern=False
                for otherNewPat in newFoundPatterns:
                    if newPatt != otherNewPat:
                        if is_subPattern(newPatt, parent=otherNewPat):
                            isSubPattern = True
                            break
                if isSubPattern is True:
                    newFoundPatterns.remove(newPatt)
                    continue # end this newPatts iteration
                # -- check if newPatt is subPat of another pattern in [gatheredPatterns]:--
                isSubPattern=False
                for oldPat in gatheredPatterns:
                    #Note: i don't even know if this actually ever drops anything due to the already-happened filtering.
                    if newPatt != oldPat:
                        if is_subPattern(newPatt, parent=oldPat):
                            isSubPattern = True
                            break
                if isSubPattern is True:
                    continue # end this newPatts iteration

                # (if it isn't a subPatt or samePatt, it reaches this point)
                # -- filter the gatheredPatterns such that none of them are subPatterns of newPat: --
                nextGatherList.append(newPatt)
                for oldPat in gatheredPatterns:
                    if not is_subPattern(oldPat, parent=newPatt):
                        nextGatherList.append(oldPat)
                gatheredPatterns=nextGatherList

        # --- filter to only keep minimumGroupSize ---
        groupSizeFilteredResults=[]
        sizeSorted=sorted(gatheredPatterns, key=lambda patt: patt.reprStr.__len__(),    reverse=True)
        groupSorted=sorted(sizeSorted,      key=lambda patt: patt.occurances.__len__(), reverse=True)
        for ID,patt in enumerate(groupSorted):
            if patt.occurances.__len__() >=MINIMUM_GROUPSIZE:
                groupSizeFilteredResults.append(patt)
                if verbose:
                    output(f"{ID=}   {patt.reprStr.__len__()} letters   {patt.occurances.__len__()} occurrences")
                    patt.print_pattern(cyphertext_whole)

        if verbose:
            output(f"found a total of {len(groupSizeFilteredResults)} Groups of matching Lymm Patterns.")
        return groupSizeFilteredResults

    # DONE, Works---
    @staticmethod
    def __gather_gapDB_of_line(line: str, gapSizes: list[int], unlimitedMode=False) -> list[list[int]]:
        """
        :param: gapSizes: ONLY those gapSizes will be checked.
        :param: unlimitedMode: if TRUE, ALL gapSizes will be checked.
        :returns: a LIST, that contains a List of gapSizes at each Positions index
        """
        textlen = line.__len__()
        resultList = []
        for position in range(0, textlen):  # for each letter of the Text...
            currLetter = line[position]
            currPossesGapList = []
            toCheckSizes = gapSizes
            if unlimitedMode is True:
                remainingLength = textlen-position
                toCheckSizes=range(0, remainingLength)
            for gapSize in toCheckSizes:
                gapOffset = gapSize + 1
                if position+gapOffset < line.__len__(): #  (just to make sure that the remaining text is even long enough for that gapsize...)
                    secondLetter = line[position+gapOffset]
                    if currLetter == secondLetter:  #  if there indeed is a letter at that position...
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
            output(f"{resultColor}{currLetter}{Style.RESET_ALL}", end='')
        output("")  # linebreaker

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
                    output(currLetter, end="")
                    continue
                for otherline in lines:
                    if otherline != line:
                        if position < otherline.__len__():
                            otherLetter = otherline[position]
                            if otherLetter == currLetter:
                                is_aligned = True
                                break
                if is_aligned:
                    output(f"{Back.GREEN}{currLetter}{Back.RESET}", end="")
                else:
                    output(currLetter, end="")
            output("")  # a linebreak

    @staticmethod
    def print_all_into_one_ciphertext(cyphertext_whole: str, LymmPatterns:list[multiLymmPattern], gapColorDict: dict):
        """
        Marks ALL given LymmPatterns on a given Ciphertext.
        Can cause severe overlap and look ugly.
        """

        def __mark_one_Lymm_pattern_listified(listified_text: list[str],
                                              LymmPairList: list[LymmPair],
                                              gapColorDict: dict,
                                              maskOffset: int):
            """
            MODIFIES the listified_text by adding colorama-colorcodes to the marked indexes.
            This is useful because it allows multiple marking-passes over the same ciphertextLine, as long as
            you didn't convert it back to a string yet.
            """
            def mark_letter(listified_string: list[str], index: int, colorCode: str):
                listified_string[index] = colorCode + listified_string[index] + Style.RESET_ALL
            for pair in LymmPairList:  # for each Gap, mark both of its letters in the respective color
                leftLetter_pos = pair.index + maskOffset
                gapSize = pair.gapsize
                rightLetter_pos = leftLetter_pos + pair.pairOffset
                colorcode = gapColorDict[gapSize]
                mark_letter(listified_text, leftLetter_pos, colorcode)
                mark_letter(listified_text, rightLetter_pos, colorcode)

        lines = cyphertext_whole.split("\n")
        for lineID in range(0, lines.__len__()):
            listified = list(lines[lineID])
            for currPattern in LymmPatterns:
                for currLineID, currLineOffset in currPattern.messageDescrs:
                    if lineID == currLineID:
                        __mark_one_Lymm_pattern_listified(listified, currPattern.LymmPairs, gapColorDict, currLineOffset)
            output("".join(listified))

    # DONE, Works---
    @staticmethod
    def __mark_one_Lines_GapDB(cipherLine: str, thisLines_gapDB:list[list[int]], gapColorDict: dict, maskOffset: int)->str:
        """
        Goes over the provided String and adds coloring to all the characters that are in a Gap
        in the provided gapDB.
        UNUSED as of now, but might be usefull someday to mark Isomorphs when you only have gapDBs at your disposition.
        """

        def mark_letter(listified_string: list, index: int, colorCode: str):
            listified_string[index] = colorCode + listified_string[index] + Style.RESET_ALL

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
        cipherLines = cyphertext_whole.split("\n")
        # ----- prepare the GapDBs -----
        each_lines_GapDB = []  # this will be one entry for each Line-ID, ergo an entry is a list, mapping  position->Gaps
        for lineID in range(0, cipherLines.__len__()):
            currLine = cipherLines[lineID]
            #(this time, they will be used only for the breakerDB, meaning that i need to check ALL gapsizes)
            currDB = Pattern_scanner.__gather_gapDB_of_line(currLine, gapSizes=None, unlimitedMode=True)  #Note: gapSizes is set to None because it is unlimitedMode anyways.
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
