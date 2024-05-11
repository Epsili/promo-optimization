from typing import ClassVar
from pydantic import BaseModel


class CSP(BaseModel):

    variables: ClassVar = []
    domains: ClassVar = {}

    slotsSegments: ClassVar = []
    promos: ClassVar = []

    @staticmethod
    def set_domain_variables(dfSchedule, dfPromos):
        # select relevant columns
        CSP.slotsSegments = (dfSchedule[["slot", "segment", "total_airtime_seconds", "reach_avg_seconds", "target_audience"]]).values.tolist()
        CSP.promos = (dfPromos[["campaign", "priority", "promo_duration_seconds", "target_audience"]]).values.tolist()

        # add no promo (that can go anywhere) because some slots/segment will need to be empty
        noPromo = [0, "", 0, "female/male"]
        CSP.promos.append(noPromo)

        # get domain for all variables (possible slots)
        for slotSegment in CSP.slotsSegments:
            variable = (int(slotSegment[0]), int(slotSegment[1]), float(slotSegment[2]), float(slotSegment[3]))
            variableTargetAudience = str(slotSegment[4])

            CSP.variables.append(variable)

            CSP.domains[variable] = []

            # HARD CONSTRAINT 1: target audience
            # remove possible slots that do not satisfy target audience constraint
            for promo in CSP.promos:
                domain = [(int(promo[0]), str(promo[1]), float(promo[2]))]
                promoTargetAudience = str(promo[3])

                if promoTargetAudience == "female/male":
                    CSP.domains[variable].append(domain)
                elif (promoTargetAudience == "female") and (variableTargetAudience == "female"):
                    CSP.domains[variable].append(domain)
                elif (promoTargetAudience == "male") and (variableTargetAudience == "male"):
                    CSP.domains[variable].append(domain)

    # HARD CONSTRAINT 2: airtime
    @staticmethod
    def constraint_airtime(var, value, assignment):
        # start with totalAirtime = airtime of the current variable/value pair
        totalAirtime = value[0][2]
        maxTotalAirtime = var[2]

        # calculate total airtime for the relevant slot
        for key in assignment.keys():
            if key[0] == var[0]:
                totalAirtime += assignment[key][0][2]

        # make sure the sum of durations of promos in the slot do not exceed slot airtime
        if totalAirtime <= maxTotalAirtime:
            return True
        else:
            return False

    # HARD CONSTRAINT 3: priority reach
    @staticmethod
    def constraint_priority(var, value, assignment):
        totalReachHighPriority = 0
        totalReachMediumPriority = 0
        totalReachLowPriority = 0

        priority = value[0][1]
        promoDurationSeconds = value[0][2]
        reachAvgSecond = var[3]
        totalReach = promoDurationSeconds * reachAvgSecond

        # start with the reach of the variable/value pair that we are currently assigning
        if priority == "H":
            totalReachHighPriority += totalReach
        elif priority == "M":
            totalReachMediumPriority += totalReach
        elif priority == "L":
            totalReachLowPriority += totalReach

        # calculate total priority reach for high/medium/low
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

        # make sure that totalReachHighPriority > totalReachMediumPriority > totalReachLowPriority
        # note: give some leeway at the start where we are just starting to assign priorities (this will be corrected automatically with every check)
        if len(assignment.keys()) < 10:
            if (totalReachHighPriority >= totalReachMediumPriority) and (
                    totalReachMediumPriority >= totalReachLowPriority):
                return True
            else:
                return False

        if (totalReachHighPriority > totalReachMediumPriority) and (totalReachMediumPriority > totalReachLowPriority):
            return True
        else:
            return False

    # HARD CONSTRAINT 4: show all promos
    @staticmethod
    def constraint_show_all_promos(var, value, assignment):
        assignmentNext = assignment.copy()
        assignmentNext[var] = value

        # get assigned promos and all promos
        assignedPromos = [p[0][0] for p in assignmentNext.values()]
        possiblePromos = [p[0] for p in CSP.promos]

        # if this is the last promo to assign in the assignment, make sure we assigned every promo at least once
        if len(assignedPromos) == len(CSP.variables):
            assignedPromosReal = [p for p in assignedPromos if p != 0]
            possiblePromosReal = [p for p in possiblePromos if p != 0]

            if len(set(assignedPromosReal)) == len(set(possiblePromosReal)):
                return True
            else:
                return False
        else:
            return True

    # OPTIMIZATION 1: slot variety
    @staticmethod
    def optimization_slot_variety(var, value, assignment):
        assignmentNext = assignment.copy()
        assignmentNext[var] = value

        slotSegmentsNum = len([v for v in CSP.variables if v[0] == var[0]])

        slotSegmentsCurrent = [v for v in assignmentNext.keys() if v[0] == var[0]]
        slotSegmentsCurrentNum = len(slotSegmentsCurrent)

        # if this is the last promo to assign to a slot, make sure that every promo can be seen at least 1 in the slot
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

    # OPTIMIZATION 2: max airtime
    @staticmethod
    def optimization_max_airtime(var, value, assignment):
        assignmentNext = assignment.copy()
        assignmentNext[var] = value

        slotSegments = [v for v in CSP.variables if v[0] == var[0]]
        slotSegmentsNum = len(slotSegments)

        slotSegmentsCurrent = [v for v in assignmentNext.keys() if v[0] == var[0]]
        slotSegmentsCurrentNum = len(slotSegmentsCurrent)

        # if this is the last promo to assign to a slot, make sure that the assigned promos are as close as possible to the max allowed airtime for the slot
        if slotSegmentsNum == slotSegmentsCurrentNum:
            maxTotalAirtime = var[2]
            totalAirtime = 0
            for key in slotSegmentsCurrent:
                totalAirtime += assignmentNext[key][0][2]

            airtimePercentageFilled = (float(totalAirtime) / float(maxTotalAirtime)) * 100.0

            # heuristic value: best solution gives us slightly more than 92% of total air time reached for all slots
            if airtimePercentageFilled > 92:
                return True
            else:
                return False
        else:
            return True

    # OPTIMIZATION 3: consecutive promos
    @staticmethod
    def optimization_consecutive_promos(var, value, assignment):
        assignmentNext = assignment.copy()
        assignmentNext[var] = value

        assignmentNextSorted = {key: assignmentNext[key] for key in
                                sorted(assignmentNext.keys(), key=lambda x: (x[0], x[1]))}

        promosSorted = [p[0][0] for p in assignmentNextSorted.values()]

        # make sure that the assignment does not show 2 promos consecutively for all slots
        hasSamePromoConsecutively = False
        for i in range(0, len(promosSorted) - 1):
            currentPromo = promosSorted[i]
            nextPromo = promosSorted[i + 1]

            # assignment allowed to show "no promo" consecutively
            if (currentPromo != 0) and (nextPromo != 0) and (currentPromo == nextPromo):
                hasSamePromoConsecutively = True
                break

        if hasSamePromoConsecutively:
            return False
        else:
            return True

    # OPTIMIZATON 4: highest airtime at segment with highest reach
    @staticmethod
    def optimization_highest_airtime_highest_reach(var, value, assignment):
        assignmentNext = assignment.copy()
        assignmentNext[var] = value

        slotSegments = [v for v in CSP.variables if v[0] == var[0]]
        slotSegmentsNum = len(slotSegments)

        slotSegmentsCurrent = [v for v in assignmentNext.keys() if v[0] == var[0]]
        slotSegmentsCurrentNum = len(slotSegmentsCurrent)

        # if this is the last promo to assign to a slot, make sure that we are assigning the promo with the longest duration to the segment with the highest reach
        if slotSegmentsNum == slotSegmentsCurrentNum:
            campaigns = []
            for slotSegment in slotSegmentsCurrent:
                campaign = (
                    slotSegment[0],
                    slotSegment[1],
                    slotSegment[3],
                    assignmentNext[slotSegment][0][0],
                    assignmentNext[slotSegment][0][2]
                )

                campaigns.append(campaign)

            # sort slot/campaign combinations by reach and by airtime, and make sure that they are the same order
            campaignsSortedOnReach = sorted(campaigns, key=lambda x: x[2])
            campaignsSortedOnAirtime = sorted(campaigns, key=lambda x: x[4])

            if campaignsSortedOnReach == campaignsSortedOnAirtime:
                return True
            else:
                return False

        return True

    # backtracking: recursive algorithm to solve the CSP problem
    @staticmethod
    def backtrack(assignment):
        # finish when we assign all promos
        if len(assignment) == len(CSP.variables):
            return assignment

        var = CSP.select_unassigned_variable(assignment=assignment)

        # if the solution is consistent, go to the next slot/segment, otherwise backtrack
        for value in CSP.domains[var]:
            if CSP.is_consistent(var, value, assignment):
                assignment[var] = value

                result = CSP.backtrack(assignment)

                if result is not None:
                    return result

                del assignment[var]

        return None

    # the next slot/segment is selected based on which one has the smallest number of potential promotions left
    # this makes sure that we take care of the cases with the smallest domain first
    @staticmethod
    def select_unassigned_variable(assignment):
        unassignedVariables = [var for var in CSP.variables if var not in assignment]
        return min(unassignedVariables, key=lambda var: len(CSP.domains[var]))

    # checks if the assignment is consistent
    @staticmethod
    def is_consistent(var, value, assignment):
        # three hard constraints (we have to keep these)
        constraintAirtimeCheck = CSP.constraint_airtime(var, value, assignment)
        constraintPriorityCheck = CSP.constraint_priority(var, value, assignment)
        constraintShowAllPromos = CSP.constraint_show_all_promos(var, value, assignment)

        # four optimizations (we can try different combinations of these)
        # note: we can try difference combinations based on which optimizations make sense
        optimizationSlotVariety = CSP.optimization_slot_variety(var, value, assignment)
        optimizationMaxAirtime = CSP.optimization_max_airtime(var, value, assignment)
        optimizationConsecutivePromos = CSP.optimization_consecutive_promos(var, value, assignment)
        optimizationHighestAirtimeHighestReach = CSP.optimization_highest_airtime_highest_reach(var, value, assignment)

        # note: this is the setup that gives the best solution (solution with highest overall reach)
        if constraintAirtimeCheck and constraintPriorityCheck and constraintShowAllPromos and optimizationMaxAirtime:
            return True
        else:
            return False

    # trigger the backtracking process to solve the CSP problem
    @staticmethod
    def solve():
        assignment = {}
        solution = CSP.backtrack(assignment=assignment)
        return solution



