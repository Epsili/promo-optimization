from promo_optimizer_data_retriever import PromoOptimizerDataRetriever
from csp_model import CSP
from print_solution import print_solution

# load raw data
dfScheduleRaw = PromoOptimizerDataRetriever.load_schedule_data()
dfPromosRaw = PromoOptimizerDataRetriever.load_promo_data()

# data preparation
dfSchedule = PromoOptimizerDataRetriever.prepare_schedule_data(dfSchedule=dfScheduleRaw)
dfPromos = PromoOptimizerDataRetriever.prepare_promos_data(dfPromos=dfPromosRaw)

# set domain variables in CSP model
CSP.set_domain_variables(dfSchedule=dfSchedule, dfPromos=dfPromos)

# solve CSP problem and get solution
solution = CSP.solve()

# print solution
print_solution(solution)






