# imports
import os
# import io
import re
# import tokenize
# import json
# import numpy as np
import pandas as pd
# import stringdist

from src_reader_writer import get_filename_for_row, get_file_src, get_file_comments


def analyze_col_freq(df_files, out_path, save_csv=False):
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

    return unique_counts


def match_all_contracts_from_src_string(src_string):
    regex = "contract .*{\n"
    matches = re.findall(regex, src_string)
    contract_names = []
    inherited_contracts = []
    for match in matches:
        match = match[len("contract "):-len("{\n")]
        match_type = match.split(' is ')
        contract_names.append(match_type[0].strip())
        if len(match_type) > 1:
            inherited_contracts.append([x.strip() for x in match_type[1].split(',')])
        else:
            inherited_contracts.append([])
    return contract_names, inherited_contracts


def match_contract_name_from_src_string(src_string):
    return match_all_contracts_from_src_string(src_string)[0]


def match_inherited_contracts_from_src_string(src_string):
    return match_all_contracts_from_src_string(src_string)[1]


def run_analysis():
    # DATA_PATH = '/home/ourownstory/Documents/SOL/derived/'
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/'
    data_path = OUT_PATH + 'cleaned/'

    df = pd.read_csv(OUT_PATH + 'df_files.csv', na_values=[])
    df.fillna('')

    _ = analyze_col_freq(df, out_path=OUT_PATH, save_csv=True)
    # print _

    df = df.apply(get_file_src, axis=1, args=(data_path, True))



if __name__ == '__main__':
    # print "hello, what are you looking for?"
    run_analysis()
