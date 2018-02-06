import os

from reader_writer import create_filenames_df, get_file_src_and_comments, save_df_with_some_cols_as_len, save_src_to
from src_processor import analyse_src_contracts, analyse_src_imports
from utils import analyse_col_freq, flatten
from import_matcher import match_imports_with_files


def get_metrics_for_project(data_path, save_path, project_class, company_name, verbose=False):
    # WIP
    metrics = {}
    # get the df with basic infos for import matching
    df_files = get_df_files(data_path, save_path, project_class, company_name)

    # all zeppelin files for importing files from there.
    # Note: assumes zeppelin is in data_path
    df_zeppelin = get_df_files(
        data_path, save_path, project_class='Zeppelin', company_name='Zeppelin', verbose=False)

    # get inheritance depth and joined src and comment files
    df = match_imports_with_files(df_files, df_zeppelin)

    return metrics


def get_df_files(data_path, save_path, project_class, company_name, verbose=False):
    # get files-df for specific project
    class_company = (project_class, company_name)
    do_save = save_path is not None
    df = create_filenames_df(
        data_path=os.path.join(data_path, project_class, company_name),
        out_path=save_path,
        save_csv=do_save,
        given_class_company=class_company,
    )
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
        project_class='Zeppelin',
        company_name='Zeppelin',
        verbose=True,
    )


if __name__ == '__main__':
    test()
