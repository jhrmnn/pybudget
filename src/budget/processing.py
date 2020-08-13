# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pandas as pd


def process_daily(df):
    df = df[~pd.isna(df['date'])]  # drop empty rows
    df = df.convert_dtypes(convert_integer=False)
    df = df.astype({'type': 'category'})
    df.loc(1)['amount':] = df.loc(1)['amount':].fillna(0)
    # checks
    misplaced_type = df[(df['amount'] != 0) == pd.isna(df['type'])]
    if len(misplaced_type):
        pass
    misplaced_charge = df[(df['amount'] != 0) == pd.isna(df['charge'])]
    if len(misplaced_charge):
        pass
    wrong_total = df[df.iloc(1)[5:].sum(axis=1) != df['amount']]
    if len(wrong_total):
        pass
    # end checks
    df = df.drop(columns='amount')  # drop totals
    return df
