# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import datetime
from itertools import product

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta


def add_charge_span(r):
    if isinstance(r['charge'], int):
        start = datetime.date(r['year'], r['charge'], 1)
        rng = start, start + relativedelta(months=1, days=-1)
    elif isinstance(r['charge'], str):
        value, unit = (
            int(r['charge'][:-1]),
            {'m': 'months', 'y': 'years'}[r['charge'][-1]],
        )
        date = r['date'].date()
        start = date + relativedelta(days=-date.day + 1)
        rng = start, start + relativedelta(days=-1, **{unit: value})
    else:
        assert r['total'] == 0
        rng = (None, None)
    r['charge_start'], r['charge_end'] = rng
    return r


def in_closed_interval(x, start, end):
    return (start <= x) & (x <= end)


def get_total(x):
    return x.assign(total=lambda x: x.iloc[:, 4:].sum(axis=1)).pipe(
        lambda x: pd.concat([x.iloc[:, :4], x['total']], axis=1)
    )


def all_records(sheets):
    return (
        pd.concat(
            [
                get_total(sheet).assign(year=int(y))
                for y, sheet in sorted(sheets.items())
                if y[:2] == '20'
            ]
        )
        .apply(add_charge_span, axis=1)
        .assign(
            charge_len=lambda x: (
                (x['charge_end'] - x['charge_start']) / np.timedelta64(1, 'M')
            )
            .round()
            .astype('Int64')
        )
        .assign(per_month=lambda x: x['total'] / x['charge_len'])
    )


def get_range(records, start=None, end=None, year=None):
    if year:
        assert not start and not end
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
    else:
        start = start or records['charge_start'].dropna().min()
        end = end or datetime.date.today()
    return start, end


def summary(records, start=None, end=None, year=None):
    start, end = get_range(records, start, end, year)
    return (
        pd.concat(
            {
                (date.year, date.month): records.loc[
                    lambda x: in_closed_interval(
                        date, x['charge_start'], x['charge_end'],
                    )
                ]
                .groupby('type')['per_month']
                .sum()
                for date in pd.date_range(start, end, freq='MS')
            },
            names=['year', 'month'],
        )
        .unstack('type')
        .fillna(0)
    )


def subs_future(records, start=None, end=None, year=None):
    start, end = get_range(records, start, end, year)
    return pd.Series(
        {
            (date.year, date.month): -records.loc[
                lambda x: x['charge_len'].fillna(0) > 1
            ]
            .loc[
                lambda x: in_closed_interval(date, x['charge_start'], x['charge_end'])
            ]['per_month']
            .sum()
            for date in pd.date_range(start, end, freq='MS')
        },
    ).rename_axis(['year', 'month'], axis=0)
