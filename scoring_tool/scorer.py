import re

from utils import flatten
from analyser import count_project_indicators_ICO, count_project_indicators_token
from tokenizer import get_token_freq


def compute_score_from_metrics(metrics, weights):
    """
    computes a normalized score from norm_metrics
    Args:
        metrics (): dict of normalized metrics, assumed to each be in range 0 to 1
        weights (): dict of weights corresponding to metrics, do not have to be normalized

    Returns:
        score, float in range 0 to 1
        weighted_metrics, contribution of each metric to score
    """
    # sanity check
    keys_diff = set(metrics.keys()) - set(weights.keys())
    # TODO: allow to ommit some metrics by not defining the weight and just warn
    if len(keys_diff) > 0:
        raise KeyError("no weight provided for metric or missing metric: {}".format(keys_diff))

    total_weight = sum([abs(x) for x in weights.values()])
    weighted_metrics = {}
    for key, value in metrics.items():
        if weights[key] >= 0:
            weighted_metrics[key] = value * weights[key] / (1.0 * total_weight)
        else:
            # negative metric means that score has to be inverted
            weighted_metrics[key] = (1.0 - value) * abs(weights[key]) / (1.0 * total_weight)

    score = sum(weighted_metrics.values())

    return score, weighted_metrics


def normalize_metrics(metrics, categoric_norm, numeric_norm):
    """
    Maps metrics values to normalized metric scores.
    categorical norms directly define score.
    numerical norms define score by division by maximum value
    Args:
        metrics ():
        categoric_norm ():
        numeric_norm ():

    Returns:

    """
    # sanity check
    cat_keys = categoric_norm.keys()
    num_keys = numeric_norm.keys()
    keys_diff = set(metrics.keys()) - set(cat_keys + num_keys)
    if len(keys_diff) > 0:
        raise KeyError("no norm provided for metric or missing metric: {}".format(keys_diff))

    norm_metrics = {}
    for key, value in metrics.items():
        if key in cat_keys:
            norm_metrics[key] = categoric_norm[key][value]
        else:
            norm_metrics[key] = max(0, min(1, value / (1.0 * numeric_norm[key])))

    return norm_metrics


def get_metric_imports_zeppelin(df, verbose):
    imports_z = df.groupby(['class', 'company'])['imports_zeppelin'].sum()
    imports_zeppelin = 'NO'
    imports_zeppelin_num = 0
    if len(imports_z) == 1:
        num_z = 1 * imports_z.iloc[0]
        if num_z > 0:
            imports_zeppelin = 'YES'
            imports_zeppelin_num = num_z / (1.0 * len(df))
    else:
        raise NotImplementedError("metric computation is implemented for one project at a time")

    if verbose:
        print "Imports Zeppelin: {} ({}/{})".format(imports_zeppelin, num_z, len(df))
    return imports_zeppelin, imports_zeppelin_num


def get_metric_inherits_per_contract(df):
    num_inheritances = []
    for i in df['inherited_contracts'].values:
        inheritances_file = [len(flatten(x)) for x in i]
        if len(inheritances_file) > 0:
            num_inheritances.extend(inheritances_file)
        else:
            num_inheritances.append(0)

    mean_inheritances = sum(num_inheritances) / (1.0 * len(num_inheritances))
    max_inheritances = max(num_inheritances)
    return mean_inheritances, max_inheritances


def get_metric_lines_per_joined_file(df, comments=False):
    if comments:
        line_lengths = df[df['is_imported'] == False]['joined_comments'].apply(lambda x: len(x.split('\n')))
    else:
        line_lengths = df[df['is_imported'] == False]['joined_src'].apply(lambda x: len(x.split('\n')))
    total_line_lengths = sum(line_lengths)
    mean_line_lengths = total_line_lengths / len(line_lengths)
    max_line_lengths = max(line_lengths)
    return total_line_lengths, mean_line_lengths, max_line_lengths


def get_metric_ICO(df, verbose):
    _, indicators = count_project_indicators_ICO(df, verbose, add_to_df=False)
    ind_binary = []
    for ind in list(indicators):
        ind_binary.append(indicators[ind].iloc[0] > 0)
    ind_num = sum(ind_binary)
    is_ico = 'NO'
    if ind_num > 0:
        is_ico = 'MAYBE'
    if ind_num >= 3:
        is_ico = 'SURE'
    return is_ico


def get_metric_token(df, verbose):
    _, indicators = count_project_indicators_token(df, verbose, add_to_df=False)
    ind_binary = []
    for ind in list(indicators):
        ind_binary.append(indicators[ind].iloc[0] > 0)
    ind_num = sum(ind_binary)
    has_token = 'NO'
    if ind_num > 0:
        has_token = 'MAYBE'
    if ind_num >= 3:
        has_token = 'SURE'
    return has_token


def get_comments_to_src_ratio(df):
    src_total, _, _ = get_metric_lines_per_joined_file(df, comments=False)
    comments_total, _, _ = get_metric_lines_per_joined_file(df, comments=True)
    ratio = comments_total / (1.0 * src_total)
    return ratio


def get_token_metrics(df):
    freq = get_token_freq(df)
    tokens_num = {
        "'function'": 0,
        "'return'": 0,
        "'returns'": 0,
        "'{'": 0,
    }
    for t in tokens_num:
        num_t = freq[freq['value'] == t]['num'].values
        if len(num_t) == 1:
            tokens_num[t] = num_t[0]
    tokens_num["return_per_returns"] = tokens_num["'return'"] / (1.0 * tokens_num["'returns'"] + 1e-9)
    del tokens_num["'return'"]
    return tokens_num


def get_string_matches(df, target_name, target_regex, include_comments=False):
    df[target_name] = df['src'].apply(lambda x: len(re.findall(target_regex, x)))
    if include_comments:
        df[target_name] = df[target_name] + df['comments'].apply(lambda x: len(re.findall(target_regex, x)))
    string_matches = df.groupby(['class', 'company'])[target_name].sum()
    return string_matches.iloc[0]


def get_regex_metrics(df):
    regex_metrics = {
        "transfer": '\.transfer\(',
        "send": '\.send\(',
        "call_value": '\.call\.value\(',
    }
    regex_metrics_with_comments = {
        "random": 'random',
    }
    for target_name, target_regex in regex_metrics.items():
        regex_metrics[target_name] = get_string_matches(df, target_name, target_regex, include_comments=False)
    for target_name, target_regex in regex_metrics_with_comments.items():
        regex_metrics[target_name] = get_string_matches(df, target_name, target_regex, include_comments=True)
    return regex_metrics


def get_all_metrics(df, verbose, len_files, len_not_imported):
    metrics = {}

    metrics['imports_zeppelin'], metrics['imports_zeppelin_ratio'] = get_metric_imports_zeppelin(df, verbose)

    metrics['num_files'] = len_files
    metrics['not_imported_ratio'] = len_not_imported / (1.0 * len_files)

    imports_depths = df[df['is_imported'] == False].groupby(['class', 'company'])['imports_depth']
    metrics['import_depth_mean'] = imports_depths.mean().iloc[0]
    metrics['import_depth_max'] = imports_depths.max().iloc[0]

    metrics['contracts_num'] = len(set(flatten(df['joined_contracts'].values)))

    metrics['inheritances_mean'], metrics['inheritances_max'] = get_metric_inherits_per_contract(df)

    metrics['lines_total'], metrics['lines_mean'], metrics['lines_max'] = get_metric_lines_per_joined_file(df)

    metrics['is_ICO'] = get_metric_ICO(df, verbose)
    metrics['has_token'] = get_metric_token(df, verbose)

    metrics['comments_to_src_ratio'] = get_comments_to_src_ratio(df)

    token_metrics = get_token_metrics(df)
    metrics.update(token_metrics)

    regex_metrics = get_regex_metrics(df)
    metrics.update(regex_metrics)

    # print list(df)
    if verbose:
        print metrics

    return metrics


def test_score():
    metrics = {
        'ico': 'notICO',
        'money': 'medium',
        'liability': 'low',
        'src_complexity': 7,
    }

    categoric_norm = {
        'ico': {'notICO': 0, 'ICO': 1},
        'money': {'low': 0.0, 'medium': 0.5, 'high': 1.0},
        'liability': {'low': 0.0, 'medium': 0.5, 'high': 1.0},
    }
    numeric_norm = {
        'src_complexity': 10,
    }

    norm_metrics = normalize_metrics(metrics, categoric_norm, numeric_norm)

    # norm_metrics = {
    #     'not_ico': 1,
    #     'money': 0.5,
    #     'liability': 1,
    #     'src_complexity': 0.3,
    # }

    weights = {
        'ico': -2,
        'money': 1,
        'liability': 1,
        'src_complexity': 2,
    }
    score, weighted_metrics = compute_score_from_metrics(norm_metrics, weights)
    print score
    print weighted_metrics


if __name__ == '__main__':
    test_score()
