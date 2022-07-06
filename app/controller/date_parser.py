# Converts a year 'yy' and date tuple '(mm, dd)' to yy-mm-dd format by default
def dateTupleToString(year_string, dateTuple, date_format="%s-%s-%s"):
    month, day = dateTuple
    month_string = numericDateToString(month)
    day_string = numericDateToString(day)
    return date_format % (year_string, month_string, day_string)


# Converts numbers to to '00' format
def numericDateToString(num):
    if num < 10:
        return "0%s" % str(num)
    else:
        return str(num)


# Converts an mlh date format i.e 'Jan 1st - 2nd', 'Jan 5th - Feb 9th', 'Dec 9th', etc.
# to a tuple that represents start to end dates ((mm,dd), (mm,dd))
def convertToDateTuple(compoundDate):
    startDate = None
    endDate = None
    splitDates = compoundDate.split("-")
    if len(splitDates) == 1:
        startDate = parseRawDate(splitDates[0].strip())
    if len(splitDates) > 1:
        startDate = parseRawDate(splitDates[0].strip())
        startDateMonth, _ = startDate
        endDate = parseRawDate(
            splitDates[1].strip(), startDateMonth=startDateMonth
        )  # noqa
    return (startDate, endDate)


# Parses a single mlh date i.e 'Jan 1st', '5th' to a date tuple (mm, dd)
# In the absence of an end date month, the start date month can be used
def parseRawDate(rawDate, startDateMonth=None):
    splitDate = rawDate.split(" ")
    # Incorrect input date
    if len(splitDate) < 1:
        return (None, None)
    # No month specified for end date, so copy start date month
    if len(splitDate) < 2:
        rawDay = splitDate[0].strip()
        day = extractNumericDay(rawDay)
        return (startDateMonth, day)
    else:
        rawMonth = splitDate[0].strip()
        rawDay = splitDate[1].strip()
        month = extractNumericMonth(rawMonth)
        day = extractNumericDay(rawDay)
        return (month, day)


# Converts a month code i.e 'Jan' to its numeric representation
def extractNumericMonth(rawMonth):
    monthRange = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthCode = 1
    for month in monthRange:
        if rawMonth == month:
            return monthCode
        monthCode = monthCode + 1
    return monthCode


# Converts an mlh day i.e '1st', '2nd', 3rd', '29th', etc. to its numeric representation
def extractNumericDay(rawDay):
    dayRange = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    # Day of month has max 2 characters
    maxLoopCount = 2
    loopCount = 0
    day = ""
    for character in rawDay:
        if character in dayRange:
            day += character
        loopCount += 1
        if loopCount == maxLoopCount:
            break
    if day == "":
        return None
    return int(day)


# Calculates a numeric date score for a date tuple i.e (mm, dd)
# Computed from month and day in the context of the same year
def computeDateScore(date):
    # Must be > 61 to offset high day range scores
    weightModifier = 62
    dateScore = 0
    if date is not None:
        month, day = date
        if month is not None:
            dateScore = dateScore + (month * weightModifier)
        if day is not None:
            dateScore = dateScore + day
    return dateScore


# Compare function for sorting date tuples i.e ((mm, dd), (mm,dd))
def compareDateTuple(dateTuple):
    # Lower scores places it higher up in the sort
    # Only compare start date score in every pair
    startDate, endDate = dateTuple
    # TODO: If same start date, perform additional sort on end date
    # Currently, something like 'Jan 1st - Dec 9th' could appear just before 'Jan 1st - 2nd'
    # Requires custom sort function
    startDateScore = computeDateScore(startDate)
    return startDateScore


# Alternate date score computation for date string formats i.e 'yy-mm-dd'
def computeDateScoreStringFormat(date, key="start", month_day_indexes=[1, 2]):
    # Lower scores places it higher up in the sort
    date_split = date[key].split("-")
    # Ignore year
    month = date_split[month_day_indexes[0]]
    day = date_split[month_day_indexes[1]]
    # Must be > 61 to offset high day range scores
    weight_modifier = 62
    return int(month * weight_modifier) + int(day)


# Function to compare mlh events (hackathons) by date in ascending order
def compareEvents(event):
    date = event["date"]
    score = computeDateScoreStringFormat(date)
    return score


# Sort events by date (ascending by default)
def sortEvents(events, reverse=False):
    return sorted(events, key=lambda e: compareEvents(e), reverse=reverse)


# Sort date tuples (ascending by default)
def sortDateTuples(date_tuples, reverse=False):
    return sorted(date_tuples, key=lambda d: compareDateTuple(d), reverse=reverse)
