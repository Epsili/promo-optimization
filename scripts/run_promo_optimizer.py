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

        if constraintAirtimeCheck:
            return True
        else:
            return False


    @staticmethod
    def solve():
        assignment = {}
        solution = CSP.backtrack(assignment=assignment)
        return solution


final = CSP.solve()


# print solution
if final is not None:
    for key in final.keys():
        print(f"{key} : {final[key]}")
















