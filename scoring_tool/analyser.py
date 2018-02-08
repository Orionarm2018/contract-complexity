import os

from reader_writer import create_filenames_df, get_file_src_and_comments, save_df_with_some_cols_as_len, save_src_to
from src_processor import analyse_src_contracts, analyse_src_imports
from utils import analyse_col_freq, flatten
from import_matcher import match_imports_with_files, recurse_imports


def get_metrics_for_project(data_path, save_path, project_class, company_name, include_zeppelin=False, verbose=False, join_all=True, max_depth=10):
    # WIP

    df_files, df_joined = get_complete_df_files(
        data_path, save_path, project_class, company_name, include_zeppelin, verbose, join_all, max_depth,
    )
    df_project = collapse_to_df_project(df_joined)
    metrics = compute_metrics_from_df_project(df_project)

    return metrics


def compute_metrics_from_df_project(df):
    # WIP

    # TODO: do some column selections, combinations
    metrics = {}
    return metrics


def collapse_to_df_project(df):
    # WIP

    # TODO: do some grouping/summing/averaging
    return df


def get_complete_df_files(data_path, save_path, project_class, company_name, include_zeppelin, verbose, join_all, max_depth):
    # WIP

    # get the df with basic infos for import matching
    df_files = get_simple_df_files(data_path, save_path, project_class, company_name, verbose)

    # all zeppelin files for importing files from there.
    # Note: assumes zeppelin is in data_path
    if include_zeppelin:
        start_idx = max(df_files.index.values) + 1
        df_zeppelin = get_simple_df_files(
            data_path, save_path, project_class='Zeppelin', company_name='Zeppelin', verbose=False, start_idx=start_idx)
        # hacky fix to have zeppelin files also analysed for nested imports
        df_files = df_files.append(df_zeppelin)
    else:
        df_zeppelin = None

    # get inheritance depth and joined src and comment files
    df = match_imports_with_files(df_files, files_zeppelin=df_zeppelin, import_only_inherited=True, verbose=verbose)
    # find idxs of nested imports
    df = recurse_imports(df, join_all, max_depth)

    # TODO: join the files here
    # df_joined = None

    if include_zeppelin:
        # Finally drop the Zeppelin files:
        df.drop(df_zeppelin.index.values, inplace=True)
        df_joined.drop(df_zeppelin.index.values, inplace=True)

    return df, df_joined


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


def test():
    DATA_PATH = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/test/'
    if not os.path.exists(OUT_PATH):
        os.mkdir(OUT_PATH)

    get_metrics_for_project(
        data_path=DATA_PATH,
        save_path=OUT_PATH,
        project_class='ICO',
        company_name='Aragon',
        include_zeppelin=True,
        verbose=True,
    )


if __name__ == '__main__':
    test()
