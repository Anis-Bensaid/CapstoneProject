import os

import numpy as np
import pandas as pd
from openpyxl import load_workbook


class ExcelBuilder:

    def __init__(self, df):
        self.df = df
        self.df["date"] = pd.to_datetime([str(x) + "-01" for x in self.df.date])
        self.df["date"] = [x.date() for x in self.df.date]

        self.neutral_coef = -0.0346
        self.positive_coef = 0.0581

        self.neutral_sd = 0.020
        self.positive_sd = 0.016
        print(os.getcwd())

    def get_grouped_df(self):
        self.grouped = self.df.groupby(
            ["elc_brand", "major_category", "application", "category", "sub_category", "date"]).sum().reset_index()
        self.grouped[
            "n_ratings"] = self.grouped.sentiment_positive + self.grouped.sentiment_neutral + self.grouped.sentiment_negative
        return True

    def get_expected_effect(self):
        mean_pos = np.log(self.grouped.sentiment_positive + 1) * self.positive_coef
        mean_neu = np.log(self.grouped.sentiment_neutral + 1) * self.neutral_coef

        mean_pos = np.mean(mean_pos * self.grouped.n_ratings / sum(self.grouped.n_ratings))
        mean_neu = np.mean(mean_neu * self.grouped.n_ratings / sum(self.grouped.n_ratings))

        est_min = mean_pos - self.positive_sd + mean_pos - self.neutral_sd
        est_max = mean_pos + self.positive_sd + mean_pos + self.neutral_sd
        return (est_min, est_max)

    def export_details(self, wb):
        months = self.df.date.unique()
        self.current_month = max(months)
        self.previous_month = min(months)

        self.df_current = self.grouped.loc[self.grouped.date == self.current_month]
        self.df_previous = self.grouped.loc[self.grouped.date == self.previous_month]

        self.df_current.to_excel(wb, sheet_name='Details - Current Month', header=None, index=False,
                                 startcol=0, startrow=2)
        self.df_previous.to_excel(wb, sheet_name='Details - Prior Month', header=None, index=False,
                                  startcol=0, startrow=2)

    def export_summary(self, wb):
        estimate = self.get_expected_effect()
        estimate = str(estimate[0]) + "-" + str(estimate[1]) + "%"
        pd.DataFrame([estimate]).to_excel(wb, sheet_name='Summary', header=None, index=False,
                                          startcol=2, startrow=3)

        current_month = self.current_month
        previous_month = self.previous_month
        month_change = self.df.groupby("date").sum()[["sentiment_positive",
                                                      "sentiment_neutral",
                                                      "sentiment_negative"]]
        month_change["total"] = month_change.sentiment_positive + month_change.sentiment_neutral + month_change.sentiment_negative
        month_change = month_change.transpose()

        month_change["Percent Change"] = (month_change[current_month] - month_change[previous_month]) / month_change[
            previous_month]
        month_change["Percent Change"] = str(np.round(month_change["Percent Change"] * 100, 2)) + "%"

        month_change.to_excel(wb, sheet_name='Summary', header=None, index=False,
                              startcol=2, startrow=6)

    def export(self):
        fn = 'OutputBuilders/Output Template.xlsx'
        outpath = "Ratings & Reviews Report.xlsx"
        writer = pd.ExcelWriter(outpath, engine='openpyxl')
        book = load_workbook(fn)
        writer.book = book
        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        self.get_grouped_df()
        self.export_details(writer)
        self.export_summary(writer)

        writer.save()
        return True
