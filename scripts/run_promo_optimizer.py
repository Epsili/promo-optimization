from store.promo_optimizer_data_retriever import PromoOptimizerDataRetriever

dfScheduleRaw = PromoOptimizerDataRetriever.load_schedule_data()
dfPromosRaw = PromoOptimizerDataRetriever.load_promo_data()

dfSchedule = PromoOptimizerDataRetriever.prepare_schedule_data(dfSchedule=dfScheduleRaw)
dfPromos = PromoOptimizerDataRetriever.prepare_promos_data(dfPromos=dfPromosRaw)


print(dfSchedule.to_string())
print(dfPromos.to_string())










