import pandas as pd
from pydantic import BaseModel


class PromoOptimizerDataRetriever(BaseModel):
    @staticmethod
    def load_schedule_data() -> pd.DataFrame:
        # load schedule data from csv file
        dfScheduleRaw = pd.read_csv("assignment_dataset.csv")
        return dfScheduleRaw

    @staticmethod
    def load_promo_data() -> pd.DataFrame:
        # load promos data from csv file
        dfPromos = pd.read_csv("promos.csv")
        return dfPromos


    @staticmethod
    def prepare_schedule_data(dfSchedule: pd.DataFrame) -> pd.DataFrame:
        # clean column names for consistency and ease-of-use
        dfSchedule = dfSchedule.rename(
            columns={
                "timestamp": "start_timestamp",
                "Slot": "slot",
                "Segment No.": "segment",
                "Total Airtime (seconds)": "total_airtime_seconds",
            }
        )

        # make all strings lowercase
        dfSchedule["target_audience"] = dfSchedule["target_audience"].apply(lambda x: x.lower())

        # make timestamp data as datetime objects
        dfSchedule["start_timestamp"] = pd.to_datetime(dfSchedule["start_timestamp"], format="%d/%m/%Y %H:%M")
        dfSchedule["end_timestamp"] = pd.to_datetime(dfSchedule["end_timestamp"], format="%d/%m/%Y %H:%M")

        # get break interval in seconds
        # note: this also checks that end_timestamp comes always after start_timestamp
        dfSchedule["break_total_seconds"] = dfSchedule.apply(
            lambda row: (row["end_timestamp"] - row["start_timestamp"]).seconds,
            axis=1
            )

        # get reach average per second
        dfSchedule["reach_avg_seconds"] = dfSchedule["reach_avg"] / 60.0

        # get total reach per slot
        # dfSchedule["total_reach"] = dfSchedule["break_total_seconds"] * dfSchedule["reach_avg_seconds"]

        return dfSchedule

    @staticmethod
    def prepare_promos_data(dfPromos: pd.DataFrame) -> pd.DataFrame:
        # clean column names for consistency and ease-of-use
        dfPromos = dfPromos.rename(
            columns={
                "Campaign": "campaign",
                "Priority": "priority",
                "Notes": "notes",
                "Target-Audience(Male/Female/Kids)": "target_audience",
                "Promo Duration Seconds": "promo_duration_seconds"
            }
        )

        # make all strings lowercase
        dfPromos["target_audience"] = dfPromos["target_audience"].apply(lambda x: x.lower())

        return dfPromos







