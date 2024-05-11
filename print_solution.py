from get_total_reach import get_total_reach

# print solution (prints assignment and total reaches)
def print_solution(solution):
    if solution is not None:
        for key in solution.keys():
            print(f"{key} : {solution[key]}")

        reachDict = get_total_reach(assignment=solution)

        reachHigh = reachDict["totalReachHigh"]
        reachMedium = reachDict["totalReachMedium"]
        reachLow = reachDict["totalReachLow"]
        reachTotal = reachDict["totalReach"]

        print("")
        print(f"Total Reach High Priority = {reachHigh}")
        print(f"Total Reach Medium Priority = {reachMedium}")
        print(f"Total Reach Low Priority = {reachLow}")
        print(f"Total Reach = {reachTotal}")

