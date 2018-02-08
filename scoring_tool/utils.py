# general utils
import os

import pandas as pd


def flatten(x):
    """flattens any nested list.
    if is not list, converts to list first.
    """
    if not isinstance(x, list):
        # print type(x)
        x = list(x)
    if isinstance(x, list) and len(x) > 0:
        while any([isinstance(subitem, list) for subitem in x]):
            x = [item for sublist in x for item in sublist]
    return x


def analyse_col_freq(df_files, out_path, save_csv=False):
    # short analysis: count unique counts of entries in each column
    # save to csv
    # TODO: make plot ICO vs notICO

    unique_counts = {}
    for col in df_files:
        if col in ['src', 'comments']:
            continue
        col_counts = pd.Series.value_counts(df_files[col], sort=True)
        unique_counts[col] = col_counts.to_dict()
        if save_csv:
            col_counts.to_csv(os.path.join(out_path, 'counts_{}.csv'.format(col)))

    return

