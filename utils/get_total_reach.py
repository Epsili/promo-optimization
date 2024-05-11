def get_total_reach(assignment):
    totalReachHigh = 0
    totalReachMedium = 0
    totalReachLow = 0

    # calculate total reach for high/medium/low promos in the given assignment
    for key in assignment.keys():
        priority = assignment[key][0][1]
        promoDurationSeconds = assignment[key][0][2]
        reachAvgSecond = key[3]
        reach = promoDurationSeconds * reachAvgSecond

        if priority == "H":
            totalReachHigh += reach
        elif priority == "M":
            totalReachMedium += reach
        elif priority == "L":
            totalReachLow += reach

    # total reach of the solution is the sum of the three priority reaches
    totalReach = totalReachHigh + totalReachMedium + totalReachLow

    # return dictionary with all totals
    reachDict = {
        "totalReachHigh": totalReachHigh,
        "totalReachMedium": totalReachMedium,
        "totalReachLow": totalReachLow,
        "totalReach": totalReach
    }

    return reachDict

