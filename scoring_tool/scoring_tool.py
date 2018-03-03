import os
import json
import argparse
import pandas as pd
from df_builder import get_complete_df_files
from scorer import normalize_metrics, compute_score_from_metrics, get_all_metrics


def get_score_for_project(
        data_path, save_path, project_class, company_name,
        categoric_norm, numeric_norm, weights,
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


def test_project_score(data_path, out_path, project_class, project_name, setup_args=None):

    project_path = os.path.join(data_path, project_class, project_name)
    if not os.path.exists(project_path):
        raise LookupError("The specified path does not exist: {}".format(project_path))

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    with open(setup_args['json_weights'], 'r') as f:
        weights = json.load(f)
    with open(setup_args['json_categoric_norm'], 'r') as f:
        categoric_norm = json.load(f)
    with open(setup_args['json_numeric_norm'], 'r') as f:
        numeric_norm = json.load(f)

    score, metrics = get_score_for_project(
        data_path=data_path,
        save_path=out_path,
        project_class=project_class,
        company_name=project_name,
        categoric_norm=categoric_norm,
        numeric_norm=numeric_norm,
        weights=weights,
        include_zeppelin=True,
        verbose=False,
        join_all=True,
        max_depth=10,
    )
    return score, metrics


def test(setup_args):
    # zeppelin_folder = '/home/ourownstory/Documents/SOL/data/Zeppelin/Zeppelin/'
    score, metrics = test_project_score(
        data_path='/home/ourownstory/Documents/SOL/data/',
        out_path='/home/ourownstory/Documents/SOL/derived/test2/',
        project_class='notICO',
        project_name='Solidified',
        setup_args=setup_args,
    )
    print metrics
    print score


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup", type=str, help="JSON filename of setup parameters")
    args = parser.parse_args()
    with open(args.setup, 'r') as f:
        setup_args = json.load(f)
    test(setup_args)
    # test_all(setup_args)


if __name__ == '__main__':
    main()
