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
        print "df columns: {}".format(list(df))

    return score, metrics


def test_project_score(data_path, out_path, project_class, project_name):

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    metrics_thresholds = {
        # 'zeppelin_many': 0.2,
    }
    categoric_norm = {
        'imports_zeppelin': {'NO': 0.0, 'YES': 1.0},
        'is_ICO': {'NO': 0.0, 'MAYBE': 0.7, 'SURE': 1.0},
        'has_token': {'NO': 0.0, 'MAYBE': 0.7, 'SURE': 1.0},
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
        "'function'": 100,
        "'return'": 100,
        "'returns'": 100,
        "'{'": 100,
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
        "'function'": 1,
        "'return'": 1,
        "'returns'": 1,
        "'{'": 1,
    }

    score, metrics = get_score_for_project(
        data_path=data_path,
        save_path=out_path,
        project_class=project_class,
        company_name=project_name,
        metrics_thresholds=metrics_thresholds,
        categoric_norm=categoric_norm,
        numeric_norm=numeric_norm,
        weights=weights,
        include_zeppelin=True,
        verbose=False,
        join_all=True,
        max_depth=10,
    )
    return score, metrics


def test():
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    score, metrics = test_project_score(
        data_path='/home/ourownstory/Documents/SOL/data/',
        out_path='/home/ourownstory/Documents/SOL/derived/test2/',
        project_class='ICO',
        project_name='Monetha',
    )
    print score
    print metrics


def test_all():
    data_path = '/home/ourownstory/Documents/SOL/data/'
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    # os.listdir(data_path)
    out_path = '/home/ourownstory/Documents/SOL/derived/test/'

    df_metrics = pd.DataFrame()
    index = 0
    for project_class in os.listdir(data_path):
        for project_name in os.listdir(os.path.join(data_path, project_class)):
            # print(project_class, project_name)
            score, metrics = test_project_score(
                data_path=data_path,
                out_path=out_path,
                project_class=project_class,
                project_name=project_name,
            )
            metrics_to_df = {
                'class': project_class,
                'company': project_name,
                'score': score,
            }
            print metrics_to_df
            metrics_to_df.update(metrics)
            df_metrics_this = pd.DataFrame.from_records([metrics_to_df])
            name_individual_df = 'df_metrics_{}_{}.csv'.format(project_class, project_name)
            df_metrics_this.to_csv(os.path.join(out_path, name_individual_df))
            # add to all projects df
            df_metrics = df_metrics.append(df_metrics_this, ignore_index=True)
            index += 1
    # save df containing all projects
    df_metrics.to_csv(os.path.join(out_path, 'df_metrics_all.csv'))
    print("All metrics:")
    print df_metrics


if __name__ == '__main__':
    # test()
    test_all()
