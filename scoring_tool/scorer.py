
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
    if len(keys_diff) > 0:
        raise KeyError("no weight provided for metric or missing metric: {}".format(keys_diff))

    total_weight = sum(weights.values())
    weighted_metrics = {}
    for key, value in metrics.items():
        weighted_metrics[key] = value * weights[key] / (1.0 * total_weight)

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


def test_score():
    metrics = {
        'not_ico': 'notICO',
        'money': 'medium',
        'liability': 'low',
        'src_complexity': 7,
    }

    categoric_norm = {
        'not_ico': {'notICO': 1, 'ICO': 0.5},
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
        'not_ico': 2,
        'money': 1,
        'liability': 1,
        'src_complexity': 2,
    }
    score, weighted_metrics = compute_score_from_metrics(norm_metrics, weights)
    print score
    print weighted_metrics


if __name__ == '__main__':
    test_score()
