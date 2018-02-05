# imports
import os
import io
import re
# import tokenize
# import json
# import numpy as np
import pandas as pd
import stringdist


def create_filenames_df(data_path, out_path, save_csv=False):
    # create a pandas dataframe with the filenames in our dataset

    df_files_dict = {
        'root': [],
        'file_name': [],
    }
    for root, subdirs, df_files in os.walk(data_path):
        for file_name in df_files:
            df_files_dict['root'].append(root[len(data_path):])
            df_files_dict['file_name'].append(file_name)

    df_files = pd.DataFrame.from_dict(df_files_dict)
    root_list = df_files['root'].values
    root_list = [root.split('/') for root in root_list]
    df_files['class'] = [r.pop(0) for r in root_list]
    df_files['company'] = [r.pop(0) for r in root_list]
    df_files['root'] = ["/".join(r) for r in root_list]
    file_name_list = df_files['file_name'].values
    df_files['extension'] = [e.split('.')[-1] for e in file_name_list]

    # filter all files that are not .sol
    df_files = df_files[df_files.pop('extension') == 'sol']

    if save_csv:
        df_files.to_csv(os.path.join(out_path, 'df_files.csv'))

    return df_files


def get_filename_for_row(row, data_path):
    # helper func to get file-path
    filename = os.path.join(
        data_path,
        row.loc['class'],
        row.loc['company'],
        row.loc['root'],
        row.loc['file_name']
    )
    return filename


def analyze_col_freq(df_files, out_path, save_csv=False):
    # short analysis: count unique counts of entries in each column
    # save to csv
    # TODO: make plot ICO vs notICO

    unique_counts = {}
    for col in df_files:
        col_counts = pd.Series.value_counts(df_files[col], sort=True)
        unique_counts[col] = col_counts.to_dict()
        if save_csv:
            col_counts.to_csv(os.path.join(out_path, 'counts_{}.csv'.format(col)))

    return unique_counts


def read_src(file_name):
    # read in contents of files as string
    # including comments
    with open(file_name, 'r') as f:
        return f.read()


def read_src_nocomments(file_name, return_only_comments=False):
    # read in contents of files as string
    # strips pragma statements and comments
    with open(file_name, 'r') as f:
        src_list = []
        comments_list = []
        for line in f.readlines():
            # skip pragma
            if re.match('pragma solidity .*;', line.strip()):
                continue
            # single or multiline comments
            if re.match('/', line.strip()) or re.match('\*', line.strip()):
                comments_list.append(line)
                continue
            # inline comments
            if re.search('//', line):
                inline_comment = re.findall('[\s]*//.*\n', line)
                comments_list.extend(inline_comment)
                line = re.sub('[\s]*//.*\n', '\n', line)
                continue

            # add current src line
            src_list.append(line)

        if return_only_comments:
            return ''.join(comments_list)
        else:
            return ''.join(src_list)


def read_src_only_comments(file_name):
    # read in contents of files as string
    # strips pragma statements and comments
    with open(file_name, 'r') as f:
        # TODO
        return ''.join(src_list)


def get_file_src(row):
    return read_src(get_filename_for_row(row))


def get_file_src_nocomments(row):
    return read_src_nocomments(get_filename_for_row(row))


def get_file_src_only_comments(row):
    return read_src_nocomments(get_filename_for_row(row), return_only_comments=True)


def run_on_local_files():
    # paths
    data_path = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    # os.listdir(zeppelin_folder)
    out_path = '/home/ourownstory/Documents/SOL/derived/'

    # run
    df = create_filenames_df(data_path, out_path, save_csv=True)
    _ = analyze_col_freq(df, out_path, save_csv=True)


if __name__ == '__main__':
    run_on_local_files()

