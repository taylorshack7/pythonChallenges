# FreeCodeCamp (FCC) python daily challenge #175 Digital Detox
# Completed 2/5/26
# Instructions:
# Given an array of your login logs, determine whether you have met your digital detox goal.
# Each log is a string in the format "YYYY-MM-DD HH:mm:ss".
# You have met your digital detox goal if both of the following statements are true:
# 1. You logged in no more than once within any four-hour period.
# 2. You logged in no more than 2 times on any single day.
def digital_detox(logs):
    #sort the logs & set control variable to first log entry
    logs.sort()
    control = logs[0]
    #Parse through datetime string and set year, month, day, hour, minute, and seconds to a corresponding variable
    year1 = int(logs[0][0:4])
    month1 = int(logs[0][5:7])
    day1 = int(logs[0][8:10])
    hour1 = int(logs[0][11:13])
    minutes1 = float(logs[0][14:16])/60
    seconds1 = float(logs[0][-2:])/3600
    #Create loop variables to check if detox met
    detoxed = True
    count = 1
    #Loop thru list of logins, setting comparison variables
    for login in logs:
        year2 = int(login[0:4])
        month2 = int(login[5:7])
        day2 = int(login[8:10])
        hour2 = int(login[11:13])
        minutes2 = (float(login[14:16])/60)
        seconds2 = (float(login[-2:])/3600)
        #Decision tree to check if more than one login in a 4 hour period.
        if year2 - year1 == 0 and month2 - month1 == 0 and day2 - day1 == 0 and control != login:
            time = (hour2 - hour1) + (minutes2 - minutes1) + (seconds2 - seconds1)
            if time <= 4:
                detoxed = False
        elif year2 - year1 == 0 and month2 - month1 == 0 and day2 - day1 == 1 and hour2 - (hour1 + 24) <= 4 and control != login:
            time = ((hour2 + 24) - hour1) + (minutes2 - minutes1) + (seconds2 - seconds1)
            if time <= 4:
                detoxed = False
        #decison tree to check if more than 2 logins on a single day
        if year2 - year1 == 0 and month2 - month1 == 0 and day2 - day1 == 0 and control != login:
            count +=1
            if count > 2:
                detoxed = False
        if (year2 - year1 > 0 or month2 - month1 > 0 or day2 - day1 > 0) and control != login:
            count = 1
        year1 = year2
        month1 = month2
        day1 = day2
        hour1 = hour2
        minutes1 = minutes2
        seconds1 = seconds2
        control = login
    return detoxed


#True
print(digital_detox(["2026-02-01 08:00:00", "2026-02-01 12:30:00"]))
#False
print(digital_detox(["2026-02-01 04:00:00", "2026-02-01 07:30:00"]))
#True
print(digital_detox(["2026-01-31 08:21:30", "2026-01-31 14:30:00", "2026-02-01 08:00:00", "2026-02-01 12:30:00"]))
#False
print(digital_detox(["2026-01-31 10:40:21", "2026-01-31 15:19:41", "2026-01-31 21:49:50", "2026-02-01 09:30:00"]))
#True
print(digital_detox(["2026-02-05 10:00:00", "2026-02-01 09:00:00", "2026-02-03 22:15:00", "2026-02-02 12:10:00", "2026-02-02 07:15:00", "2026-02-04 09:45:00", "2026-02-01 16:50:00", "2026-02-03 09:30:00"]))
#False
print(digital_detox(["2026-02-05 10:00:00", "2026-02-01 09:00:00", "2026-02-03 22:15:00", "2026-02-02 12:10:00", "2026-02-02 07:15:00", "2026-02-04 01:45:00", "2026-02-01 16:50:00", "2026-02-03 09:30:00"]))
