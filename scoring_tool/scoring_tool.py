import os
import pandas as pd
from df_builder import get_complete_df_files
from scorer import normalize_metrics, compute_score_from_metrics, get_all_metrics


def get_score_for_project(
        data_path, save_path, project_class, company_name,
        metrics_thresholds, categoric_norm, numeric_norm, weights,
        include_zeppelin=False, verbose=False, join_all=True, max_depth=10,):
    # WIP

    df, len_files, len_not_imported = get_complete_df_files(
        data_path, save_path, project_class, company_name, include_zeppelin, verbose, join_all, max_depth,
    )
    metrics = get_all_metrics(df, verbose, len_files, len_not_imported)
    metrics_norm = normalize_metrics(metrics, categoric_norm, numeric_norm)
    score, weighted_metrics = compute_score_from_metrics(metrics_norm, weights)

    if verbose:
        print "Score: {}".format(score)

    return score, metrics


def test_project_score(DATA_PATH, OUT_PATH, project_class, project_name):

    if not os.path.exists(OUT_PATH):
        os.mkdir(OUT_PATH)

    metrics_thresholds = {
        # 'zeppelin_many': 0.2,
    }
    categoric_norm = {
        'imports_zeppelin': {'NO': 0.0, 'YES': 1.0},
        'is_ICO': {'NO': 0.0, 'YES': 0.7, 'SURE': 1.0},
        'has_token': {'NO': 0.0, 'YES': 0.7, 'SURE': 1.0},
    }
    numeric_norm = {
        'imports_zeppelin_num': 0.5,
        'len_files': 100,
        'not_imported_ratio': 1.0,
        'import_depth_mean': 2,
        'import_depth_max': 5,
        'contracts_num': 100,
        'inheritances_mean': 2,
        'inheritances_max': 5,
        'lines_total': 2000,
        'lines_mean': 200,
        'lines_max': 500,
        'comments_ratio': 1.0,
    }
    weights = {
        'imports_zeppelin_num': -1,
        'imports_zeppelin': -2,
        'len_files': 0,
        'not_imported_ratio': 0,
        'import_depth_mean': 0,
        'import_depth_max': 1,
        'contracts_num': 1,
        'inheritances_mean': 0,
        'inheritances_max': 1,
        'lines_total': 1,
        'lines_mean': 0,
        'lines_max': 1,
        'is_ICO': -2,
        'has_token': 1,
        'comments_ratio': -1,
    }

    score, metrics = get_score_for_project(
        data_path=DATA_PATH,
        save_path=OUT_PATH,
        project_class=project_class,
        company_name=project_name,
        metrics_thresholds=metrics_thresholds,
        categoric_norm=categoric_norm,
        numeric_norm=numeric_norm,
        weights=weights,
        include_zeppelin=True,
        verbose=True,
        join_all=True,
        max_depth=10,
    )
    return score, metrics


def test():
    DATA_PATH = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/test/'

    test_project_score(DATA_PATH, OUT_PATH, project_class='notICO', project_name='Solidified')


def test_all():
    DATA_PATH = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/test/'

    df_metrics = pd.DataFrame()
    index = 0
    for project_class in os.listdir(DATA_PATH):
        for project_name in os.listdir(os.path.join(DATA_PATH, project_class)):
            score, metrics = test_project_score(DATA_PATH, OUT_PATH, project_class, project_name)
            metrics_to_df = {}
            metrics_to_df['class'] = project_class
            metrics_to_df['company'] = project_class
            metrics_to_df['score'] = score
            metrics_to_df.update(metrics)
            df_metrics_this = pd.DataFrame.from_records([metrics_to_df])
            df_metrics = df_metrics.append(df_metrics_this, ignore_index=True)
            df_metrics_this.to_csv(os.path.join(OUT_PATH, 'df_{}_{}_{}.csv'.format('metrics', project_class, project_name)))
            index += 1

    df_metrics.to_csv(os.path.join(OUT_PATH, 'df_{}_all.csv'.format('metrics')))
    print df_metrics


if __name__ == '__main__':
    # test()
    test_all()
