from get_total_reach import get_total_reach

# print solution (prints assignment and total reaches)
def print_solution(solution):
    if solution is not None:
        print("SOLUTION (slot, segment): promo:")
        print("================================")

        sortedKeys = sorted(solution, key=lambda x: x[0])

        for key in sortedKeys:
            slot = key[0]
            segment = key[1]
            promo = solution[key][0][0]

            if promo != 0:
                print(f"({slot}, {segment}) : {promo}")
            else:
                print(f"({slot}, {segment}) : ")

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

