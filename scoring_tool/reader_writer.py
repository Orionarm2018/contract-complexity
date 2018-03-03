# imports
import os
import io
import re
# import tokenize
# import json
# import numpy as np
import pandas as pd
import stringdist


def create_filenames_df(data_path, out_path, save_csv=False, given_class_company=None):
    # create a pandas dataframe with the filenames in our dataset

    df_files_dict = {
        'root': [],
        'file_name': [],
    }
    for root, subdirs, files in os.walk(data_path):
        for file_name in files:
            df_files_dict['root'].append(root[len(data_path):])
            df_files_dict['file_name'].append(file_name)

    df_files = pd.DataFrame.from_dict(df_files_dict)
    root_list = df_files['root'].values
    root_list = [root.split('/') for root in root_list]

    if given_class_company is None:
        df_files['class'] = [r.pop(0) for r in root_list]
        df_files['company'] = [r.pop(0) for r in root_list]
    else:
        df_files['class'] = given_class_company[0]
        df_files['company'] = given_class_company[1]

    df_files['root'] = ["/".join(r) for r in root_list]
    file_name_list = df_files['file_name'].values
    df_files['extension'] = [e.split('.')[-1] for e in file_name_list]

    # filter all files that are not .sol
    df_files = df_files[df_files.pop('extension') == 'sol']

    if save_csv:
        df_files.to_csv(os.path.join(out_path, 'df_files.csv'))

    return df_files


def get_filename_for_row(row, data_path, with_root=True, comments=False):
    # helper func to get file-path
    data_path = os.path.join(
        data_path,
        row.loc['class'],
        row.loc['company'],
    )
    filename = row.loc['file_name']
    root_folders = [x for x in row.loc['root'].split('/') if x not in ['', '.', '..']]

    if not with_root:
        root_name = "_".join(root_folders)
        root_name = "{}_".format(root_name) if len(root_name) > 0 else root_name
        filename = "{}{}".format(root_name, filename)
    else:
        data_path = os.path.join(
            data_path,
            "/".join(root_folders),
        )
    if comments:
        filename = "comments_{}".format(filename)

    filename_out = os.path.join(data_path,filename)
    return filename_out


# TODO: remove
def get_filename_old_for_row(row, data_path):
    # helper func to get file-path
    filename = os.path.join(
        data_path,
        row.loc['class'],
        row.loc['company'],
        row.loc['root'],
        row.loc['file_name']
    )
    return filename


def read_src(file_name):
    # read in contents of files as string
    # including comments
    with open(file_name, 'r') as f:
        return f.read()


def read_src_nocomments(file_name, return_also_comments=False):
    # read in contents of files as string
    # strips pragma statements and comments
    with open(file_name, 'r') as f:
        src_list = []
        comments_list = []
        open_multiline_comment = False
        for line in f.readlines():
            # skip pragma
            if re.match('pragma solidity .*;', line.strip()):
                # comments_list.append(line)
                continue
            # single line comments
            if re.match('//', line.strip()):
                comments_list.append(line)
                continue
            # multiline comments: start
            if re.match('/\*', line.strip()):
                if not re.search('\*/', line.strip()):
                    open_multiline_comment = True
                comments_list.append(line)
                continue
            # multiline comments: end
            if re.match('\*/', line.strip()) or re.match('\*\*/', line.strip()):
                open_multiline_comment = False
                comments_list.append(line)
                continue
            # in-progress multiline comment
            if re.match('\*', line.strip()) or open_multiline_comment:
                if re.search('\*/', line.strip()):
                    open_multiline_comment = False
                comments_list.append(line)
                continue

            # inline comments
            if re.search('[\s]+//', line) or re.search('//[\s]+', line):
                inline_comment = re.findall('[\s]*//.*\n', line)
                comments_list.extend(inline_comment)
                line = re.sub('[\s]*//.*\n', '\n', line)

            # add current src line
            src_list.append(line)

        # add final newline
        src_list.append('\n')
        comments_list.append('\n')

        # if 'todebug.sol' in file_name:
        #     print(file_name)
        #     print(src_list)
        #     print(comments_list)

        if return_also_comments:
            return ''.join(src_list), ''.join(comments_list)
        else:
            return ''.join(src_list)


def get_file_src(row, data_path, with_root):
    row['src'] = read_src(
        file_name=get_filename_for_row(row, data_path, with_root, comments=False)
    )
    return row


def get_file_comments(row, data_path, with_root):
    row['comments'] = read_src(
        file_name=get_filename_for_row(row, data_path, with_root, comments=True)
    )
    return row


def get_file_src_nocomments(row, data_path):
    row['src'] = read_src_nocomments(
        file_name=get_filename_for_row(row, data_path),
        return_also_comments=False,
    )
    return row


def get_file_src_and_comments(row, data_path):
    row['src'], row['comments'] = read_src_nocomments(
        file_name=get_filename_for_row(row, data_path),
        return_also_comments=True,
    )
    return row


def save_df_with_some_cols_as_len(df, out_path, name, cols):
    # save without src to csv
    df_out = df.copy(deep=True)
    for column in cols:
        if column in list(df):
            df_out[column] = df[column].apply(lambda x: len(x))
    df_out.to_csv(os.path.join(out_path, 'df_{}.csv'.format(name)))


def save_src_to(row, out_path, new_name, with_root_folders=True):
    nested_folders = [new_name, row.loc['class'], row.loc['company']]
    if with_root_folders:
        root_folders = [x for x in row.loc['root'].split('/') if x not in ['', '.', '..']]
        nested_folders.extend(root_folders)

    mkdir_path = out_path
    for folder in nested_folders:
        mkdir_path = os.path.join(mkdir_path, folder)
        if not os.path.exists(mkdir_path):
            os.mkdir(mkdir_path)

    file_name = get_filename_for_row(
        row,
        data_path=os.path.join(out_path, new_name),
        with_root=with_root_folders,
        comments=False,
    )
    file_name_comments = get_filename_for_row(
        row,
        data_path=os.path.join(out_path, new_name),
        with_root=with_root_folders,
        comments=True,
    )
    if new_name == 'joined':
        src = row.loc['joined_src']
        comments = row.loc['joined_comments']
    else:
        src = row.loc['src']
        comments = row.loc['comments']

    with open(file_name, 'w')as f:
        f.write(src)
    if 'comments' in list(row.index.values):
        with open(file_name_comments, 'w')as f:
            f.write(comments)


def run_on_local_files(data_path, out_path):
    # run
    df = create_filenames_df(data_path, out_path, save_csv=True)

    df = df.apply(get_file_src_and_comments, axis=1, args=(data_path,))

    # save df
    save_df_with_some_cols_as_len(
        df, out_path=out_path, name='files', cols=['src', 'comments'])

    # save src
    _ = df.apply(save_src_to, axis=1, args=(out_path, 'cleaned'))


if __name__ == '__main__':
    DATA_PATH = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/test/'

    run_on_local_files(DATA_PATH, OUT_PATH)

