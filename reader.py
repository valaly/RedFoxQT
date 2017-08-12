# READER MODULE
# Function:
#   Transforms data to requested format
#
# Input:
#   Data to format
#   Requested format
#   Additional information regarding current and/or requested format
#
# Output:
#   Data in correct format
#
# Calls:
# Is called by:
import pandas as pd


def get_tagged_string(string, start_tag, end_tag):
    """Returns string between tags from larger string
    Input:
        string      larger string
        start_tag    tag after which desired string starts
        end_tag      tag before which desired string ends
    Output:
        desired string
    """
    start_split = string.split(start_tag)
    end_split = start_split[1].split(end_tag)

    return end_split[0]

#--- readCsvFile ---#
# Reads csv file
# Input:
#   file        csv file (including path)
# Output:
#   header      list with header
#   rowlist     list of list of rows ([[row1][row2][row3]])
#def readCsvFile(file):


