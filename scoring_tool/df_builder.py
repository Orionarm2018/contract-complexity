
import os
import pandas as pd

from reader_writer import create_filenames_df, get_file_src_and_comments, save_df_with_some_cols_as_len, save_src_to
from src_processor import analyse_src_contracts, analyse_src_imports
from utils import analyse_col_freq, flatten
from import_matcher import match_imports_with_files, recurse_imports, join_imported_files
from analyser import detect_crowdsale_presale_ICO, detect_coin_token
from analyser import count_project_indicators_token, count_project_indicators_ICO
from tokenizer import tokenize_string_from_row


def get_complete_df_files(data_path, save_path, project_class, company_name, include_zeppelin, verbose, join_all, max_depth):

    # get the df with basic infos for import matching
    df_files = get_simple_df_files(data_path, save_path, project_class, company_name, verbose)

    # all zeppelin files for importing files from there.
    # Note: assumes zeppelin is in data_path
    if include_zeppelin:
        start_idx = max(df_files.index.values) + 1
        df_zeppelin = get_simple_df_files(
            data_path, save_path=None, project_class='Zeppelin', company_name='Zeppelin', verbose=False, start_idx=start_idx)
        # hacky fix to have zeppelin files also analysed for nested imports
        df_files = df_files.append(df_zeppelin)
    else:
        df_zeppelin = None

    # get inheritance depth and joined src and comment files
    df = match_imports_with_files(df_files, files_zeppelin=df_zeppelin, import_only_inherited=True, verbose=verbose)
    # find idxs of nested imports
    df = recurse_imports(df, join_all, max_depth, verbose)
    # join src and comments, drop import lines
    df = join_imported_files(df)

    if include_zeppelin:
        # Finally drop the Zeppelin files:
        df.drop(df_zeppelin.index.values, inplace=True)

    len_files = len(df)
    len_not_imported = len(df[df['is_imported'] == False])
    if not join_all:
        # remove the imported files
        df.drop(df[df['is_imported']].index.values, inplace=True)
        if verbose:
            print "Dropped imported files: {} out of {}".format(len_files - len_not_imported, len_files)
        # overwrite src with joined_src
        df['src'] = df['joined_src']
        df['comments'] = df['joined_comments']

    if verbose:
        col_freq = pd.Series.value_counts(df['imports_depth'], sort=False)
        print "Imports Depths ({} total files):".format(len(df))
        print col_freq

    df = df.apply(detect_crowdsale_presale_ICO, axis=1)
    df = df.apply(detect_coin_token, axis=1)
    df, _ = count_project_indicators_ICO(df, verbose)
    df, _ = count_project_indicators_token(df, verbose)

    if save_path is not None:
        # save src and comments
        _ = df.apply(save_src_to, axis=1, args=(save_path, 'joined'))
        cols_not_save = ['src', 'joined_src', 'comments', 'joined_comments']
        save_df_with_some_cols_as_len(df, save_path, name='joined', cols=cols_not_save)

    df = df.apply(tokenize_string_from_row, axis=1)

    return df, len_files, len_not_imported


def get_simple_df_files(data_path, save_path, project_class, company_name, verbose=False, start_idx=None):
    # get files-df for specific project
    class_company = (project_class, company_name)
    do_save = save_path is not None
    df = create_filenames_df(
        data_path=os.path.join(data_path, project_class, company_name),
        out_path=save_path,
        save_csv=do_save,
        given_class_company=class_company,
    )
    if start_idx is not None:
        df.index = start_idx + df.index.values

    df = df.apply(get_file_src_and_comments, axis=1, args=(data_path,))

    if do_save:  # save src
        _ = df.apply(save_src_to, axis=1, args=(save_path, 'cleaned'))
    if verbose or do_save:
        unique_counts = analyse_col_freq(df, out_path=save_path, save_csv=do_save)
        if verbose:
            print "unique column value counts: ", unique_counts

    # get more features from src
    df = analyse_src_contracts(df, verbose, save_path)
    df = analyse_src_imports(df, verbose, save_path)

    if do_save:  # save df
        save_df_with_some_cols_as_len(
            df, out_path=save_path, name='files', cols=['src', 'comments'])

    return df

