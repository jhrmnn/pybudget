# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import numpy as np
import pandas as pd


def total_summary(daily_df, subs_df):
    return daily_summary(daily_df).add(subs_summary(subs_df), fill_value=0)


def daily_summary(df):
    return (
        df.groupby(['month', 'type'])
        .apply(lambda x: x.iloc(1)[4:].sum().sum())
        .unstack()
        .fillna(0)
    )


def subs_on_day(df, today):
    return (
        df.assign(
            progress=((today - df['acquired']) / np.timedelta64(1, 'M'))
            .round()
            .astype(int),
        )
        .loc(0)[lambda df: (df['progress'] > 0) & (df['progress'] <= df['n_months'])]
        .groupby('type')
        .apply(lambda df: df['per_month'].sum())
    )


def subs_summary(df):
    df = df.assign(
        n_months=lambda x: ((x['final'] - x['acquired']) / np.timedelta64(1, 'M'))
        .round()
        .astype(int)
    )
    df = df.assign(
        per_month=lambda x: (x['final_value'] - x['acquired_value']) / x['n_months']
    )
    df = (
        pd.concat(
            {
                month: subs_on_day(
                    df, np.datetime64(f'2019-{month:02d}') + np.timedelta64(1, 'M')
                )
                for month in range(1, 13)
            },
            names=['month'],
        )
        .unstack('type')
        .round()
    )
    return df
