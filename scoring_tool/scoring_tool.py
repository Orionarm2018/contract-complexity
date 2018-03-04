import os
import json
import argparse
import pandas as pd
from df_builder import get_complete_df_files
from scorer import normalize_metrics, compute_score_from_metrics, get_all_metrics


def get_project_score(setup_args, project_class, project_name):
    data_path = setup_args["data_path"]
    out_path = setup_args["out_path"]

    if not setup_args["save_results"]:
        setup_args["out_path"] = None

    project_path = os.path.join(data_path, project_class, project_name)
    if not os.path.exists(project_path):
        raise LookupError("The specified path does not exist: {}".format(project_path))

    if out_path is not None and not os.path.exists(out_path):
        os.mkdir(out_path)

    df, len_files, len_not_imported = get_complete_df_files(
        setup_args,
        project_class=project_class,
        company_name=project_name,
    )
    metrics = get_all_metrics(df, setup_args["verbose"], len_files, len_not_imported)
    metrics_norm = normalize_metrics(metrics, setup_args["categoric_norm"], setup_args["numeric_norm"])
    score, weighted_metrics = compute_score_from_metrics(metrics_norm, setup_args["weights"])

    if setup_args["verbose"]:
        print "Score: {}".format(score)
        print "df columns: {}".format(list(df))

    return score, metrics


def test_all(setup_args):
    data_path = setup_args["data_path"]
    out_path = setup_args["out_path"]

    df_metrics = pd.DataFrame()
    index = 0
    for project_class in os.listdir(data_path):
        for project_name in os.listdir(os.path.join(data_path, project_class)):
            # print(project_class, project_name)
            score, metrics = get_project_score(
                setup_args=setup_args,
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

            if setup_args["out_path"] is not None:
                name_individual_df = 'df_metrics_{}_{}.csv'.format(project_class, project_name)
                df_metrics_this.to_csv(os.path.join(out_path, name_individual_df))

            # add to all projects df
            df_metrics = df_metrics.append(df_metrics_this, ignore_index=True)
            index += 1
    if setup_args["out_path"] is not None:
        # save df containing all projects
        df_metrics.to_csv(os.path.join(out_path, 'df_metrics_all.csv'))
    print("All metrics:")
    print df_metrics


def load_setup_args(setup_path):
    with open(os.path.join(setup_path, 'setup.json'), 'r') as f:
        setup_args = json.load(f)

    for params in ['weights', 'categoric_norm', 'numeric_norm']:
        with open(os.path.join(setup_path, '{}.json'.format(params)), 'r') as f:
            setup_args[params] = json.load(f)
    return setup_args


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup_path", type=str, default="scoring_tool/setup/",
        help="path of setup JSONs"
    )
    args = parser.parse_args()
    setup_args = load_setup_args(args.setup_path)

    # RUN single
    print(get_project_score(setup_args, 'notICO', 'Solidified'))

    # RUN all
    test_all(setup_args)


if __name__ == '__main__':
    main()
