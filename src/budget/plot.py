# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


def plot_summary(df, ax):
    df = df[df.sum().sort_values().index]
    bottom = 0
    for col in df:
        ax.bar(
            range(len(df)),
            df[col].values,
            bottom=bottom if col != 'wage' else 0,
            label=col,
        )
        bottom += df[col]
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df.index, rotation=45, ha='right')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
