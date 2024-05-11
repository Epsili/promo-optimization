from pydantic import BaseModel

from store.promo_optimizer_data_retriever import PromoOptimizerDataRetriever



dfScheduleRaw = PromoOptimizerDataRetriever.load_schedule_data()
dfPromosRaw = PromoOptimizerDataRetriever.load_promo_data()

dfSchedule = PromoOptimizerDataRetriever.prepare_schedule_data(dfSchedule=dfScheduleRaw)
dfPromos = PromoOptimizerDataRetriever.prepare_promos_data(dfPromos=dfPromosRaw)

# print(dfSchedule.to_string())
# print(dfPromos.to_string())


variables = []
domains = {}

slotsSegments = (dfSchedule[["slot", "segment", "total_airtime_seconds", "reach_avg_seconds", "target_audience"]]).values.tolist()
promos = (dfPromos[["campaign", "priority", "promo_duration_seconds", "target_audience"]]).values.tolist()

# add no promo (that can go anywhere) because some slots/segment will need to be empty
noPromo = [0, "", 0, "female/male"]
promos.append(noPromo)

for slotSegment in slotsSegments:
    variable = (int(slotSegment[0]), int(slotSegment[1]), float(slotSegment[2]), float(slotSegment[3]))
    variableTargetAudience = str(slotSegment[4])

    variables.append(variable)

    domains[variable] = []

    for promo in promos:
        domain = [(int(promo[0]), str(promo[1]), float(promo[2]))]
        promoTargetAudience = str(promo[3])

        if promoTargetAudience == "female/male":
            domains[variable].append(domain)
        elif (promoTargetAudience == "female") and (variableTargetAudience == "female"):
            domains[variable].append(domain)
        elif (promoTargetAudience == "male") and (variableTargetAudience == "male"):
            domains[variable].append(domain)



# print(variables)
#
# for key in domains.keys():
#     print(f"{key} : {domains[key]}")



def constraint_airtime(var, value, assignment):
    totalAirtime = value[0][2]
    maxTotalAirtime = var[2]

    for key in assignment.keys():
        if key[0] == var[0]:
            totalAirtime += assignment[key][0][2]

    if totalAirtime <= maxTotalAirtime:
        return True
    else:
        return False


def constraint_priority(var, value, assignment):
    totalReachHighPriority = 0
    totalReachMediumPriority = 0
    totalReachLowPriority = 0

    priority = value[0][1]
    promoDurationSeconds = value[0][2]
    reachAvgSecond = var[3]
    totalReach = promoDurationSeconds * reachAvgSecond

    if priority == "H":
        totalReachHighPriority += totalReach
    elif priority == "M":
        totalReachMediumPriority += totalReach
    elif priority == "L":
        totalReachLowPriority += totalReach

    for key in assignment.keys():
        priority = assignment[key][0][1]
        promoDurationSeconds = assignment[key][0][2]
        reachAvgSecond = key[3]
        totalReach = promoDurationSeconds * reachAvgSecond

        if priority == "H":
            totalReachHighPriority += totalReach
        elif priority == "M":
            totalReachMediumPriority += totalReach
        elif priority == "L":
            totalReachLowPriority += totalReach

    if len(assignment.keys()) < 3:
        if (totalReachHighPriority >= totalReachMediumPriority) and (totalReachMediumPriority >= totalReachLowPriority):
            return True
        else:
            return False

    if (totalReachHighPriority > totalReachMediumPriority) and (totalReachMediumPriority > totalReachLowPriority):
        return True
    else:
        return False


def constraint_show_all_promos(var, value, assignment):
    assignmentNext = assignment.copy()
    assignmentNext[var] = value

    assignedPromos = [p[0][0] for p in assignmentNext.values()]
    possiblePromos = [p[0] for p in promos]

    if len(assignedPromos) == len(variables):
        assignedPromosReal = [p for p in assignedPromos if p != 0]
        possiblePromosReal = [p for p in possiblePromos if p != 0]

        if len(set(assignedPromosReal)) == len(set(possiblePromosReal)):
            return True
        else:
            return False
    else:
        return True


def optimization_slot_variety(var, value, assignment):
    assignmentNext = assignment.copy()
    assignmentNext[var] = value

    slotSegmentsNum = len([v for v in variables if v[0] == var[0]])

    slotSegmentsCurrent = [v for v in assignmentNext.keys() if v[0] == var[0]]
    slotSegmentsCurrentNum = len(slotSegmentsCurrent)

    if slotSegmentsNum == slotSegmentsCurrentNum:
        slotCampaignsList = []
        slotCampaignsSet = set()

        for key in slotSegmentsCurrent:
            campaign = assignmentNext[key][0][0]

            if campaign != 0:
                slotCampaignsList.append(campaign)
                slotCampaignsSet.add(campaign)

        if len(slotCampaignsList) == len(slotCampaignsSet):
            return True
        else:
            return False
    else:
        return True



def optimization_max_airtime(var, value, assignment):
    assignmentNext = assignment.copy()
    assignmentNext[var] = value

    slotSegments = [v for v in variables if v[0] == var[0]]
    slotSegmentsNum = len(slotSegments)

    slotSegmentsCurrent = [v for v in assignmentNext.keys() if v[0] == var[0]]
    slotSegmentsCurrentNum = len(slotSegmentsCurrent)

    if slotSegmentsNum == slotSegmentsCurrentNum:
        maxTotalAirtime = var[2]
        totalAirtime = 0
        for key in slotSegmentsCurrent:
            totalAirtime += assignmentNext[key][0][2]

        airtimePercentageFilled = (float(totalAirtime) / float(maxTotalAirtime)) * 100.0

        if airtimePercentageFilled > 60:
            return True
        else:
            return False
    else:
        return True


def optimization_consecutive_promos(var, value, assignment):
    assignmentNext = assignment.copy()
    assignmentNext[var] = value

    assignmentNextSorted = {key: assignmentNext[key] for key in sorted(assignmentNext.keys(), key=lambda x: (x[0], x[1]))}

    promosSorted = [p[0][0] for p in assignmentNextSorted.values()]

    hasSamePromoConsecutively = False
    for i in range(0, len(promosSorted) - 1):
        currentPromo = promosSorted[i]
        nextPromo = promosSorted[i+1]

        if (currentPromo != 0) and (nextPromo != 0) and (currentPromo == nextPromo):
            hasSamePromoConsecutively = True
            break

    if hasSamePromoConsecutively:
        return False
    else:
        return True








def get_total_reach(assignment):
    # check total reach for high/medium/low
    totalReachHigh = 0
    totalReachMedium = 0
    totalReachLow = 0

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

    totalReach = totalReachHigh + totalReachMedium + totalReachLow
    return totalReach



class CSP(BaseModel):

    @staticmethod
    def backtrack(assignment):
        if len(assignment) == len(variables):
            return assignment

        var = CSP.select_unassigned_variable(assignment=assignment)

        for value in domains[var]:
            if CSP.is_consistent(var, value, assignment):
                assignment[var] = value

                result = CSP.backtrack(assignment)

                if result is not None:
                    return result

                del assignment[var]

        return None



    @staticmethod
    def select_unassigned_variable(assignment):
        unassignedVariables = [var for var in variables if var not in assignment]
        return min(unassignedVariables, key=lambda var: len(domains[var]))


    @staticmethod
    def is_consistent(var, value, assignment):
        constraintAirtimeCheck = constraint_airtime(var, value, assignment)
        constraintPriorityCheck = constraint_priority(var, value, assignment)
        constraintShowAllPromos = constraint_show_all_promos(var, value, assignment)

        optimizationSlotVariety = optimization_slot_variety(var, value, assignment)
        optimizationMaxAirtime = optimization_max_airtime(var, value, assignment)
        optimizationConsecutivePromos = optimization_consecutive_promos(var, value, assignment)

        if constraintAirtimeCheck and constraintPriorityCheck and constraintShowAllPromos and optimizationMaxAirtime and optimizationSlotVariety and optimizationConsecutivePromos:
            return True
        else:
            return False


    @staticmethod
    def solve():
        assignment = {}
        solution = CSP.backtrack(assignment=assignment)
        return solution



solution = CSP.solve()

# print solution
if solution is not None:
    for key in solution.keys():
        print(f"{key} : {solution[key]}")

    # check total reach for high/medium/low
    totalReachHigh = 0
    totalReachMedium = 0
    totalReachLow = 0

    for key in solution.keys():
        priority = solution[key][0][1]
        promoDurationSeconds = solution[key][0][2]
        reachAvgSecond = key[3]
        reach = promoDurationSeconds * reachAvgSecond

        if priority == "H":
            totalReachHigh += reach
        elif priority == "M":
            totalReachMedium += reach
        elif priority == "L":
            totalReachLow += reach

    totalReach = totalReachHigh + totalReachMedium + totalReachLow

    print("")
    print(f"Total Reach High = {totalReachHigh}")
    print(f"Total Reach Medium = {totalReachMedium}")
    print(f"Total Reach Low = {totalReachLow}")
    print(f"Total Reach = {totalReach}")

















