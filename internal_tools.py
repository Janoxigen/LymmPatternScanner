
from SETTINGS import *


def output(text:str, end="\n"):
    """
    Basically a print but it also writes to file if WRITETOFILE=TRUE.
    The output file needs to be manually created/emptied by the programmer:
    if WRITETOFILE:
        # initiate and reset outputfile contents.
        f = open(OUTPUT_LOCATION, "w")
        f.close()
    """
    print(text,end=end)
    if WRITETOFILE:
        outF = open(OUTPUT_LOCATION, "a")
        outF.write(f"{text}{end}")
        outF.close()
