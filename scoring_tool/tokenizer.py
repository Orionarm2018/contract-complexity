import StringIO
import tokenize

import pandas as pd
import numpy as np


def tokenize_string(string):
    tokens_dict = {
        'line': [],
        'line_se': [],
        'type': [],
        'value': [],
    }
    tokens_list = []
    buf = StringIO.StringIO(string)
    token_generator = tokenize.generate_tokens(buf.readline)
    for type, token, (srow, scol), (erow, ecol), line in token_generator:
        tokens_dict['line'].append(srow)
        tokens_dict['line_se'].append(((srow, scol), (erow, ecol)))
        tokens_dict['type'].append(tokenize.tok_name[type])
        tokens_dict['value'].append(repr(token))
        tokens_list.append([srow, tokenize.tok_name[type], repr(token)])

    tokens_dict['type'] = ['NL' if x == 'NEWLINE' else x for x in tokens_dict['type']]

    return tokens_dict


def tokenize_string_from_row(row):
    #     filename = get_filename_for_row(row)
    #     print filename
    tokens_dict = tokenize_string(row['src'])
    row['lines'] = tokens_dict['line_se']
    row['types'] = tokens_dict['type']
    row['values'] = tokens_dict['value']
    return row


def expand_df_tokens(df):
    lens = [len(item) for item in df['types']]
    df_expanded = pd.DataFrame( {
        "file_name": np.repeat(df['file_name'].values, lens),
        "class": np.repeat(df['class'].values, lens),
        "company": np.repeat(df['company'].values, lens),
        "root": np.repeat(df['root'].values, lens),
        "type": np.concatenate(df['types'].values),
        "value": np.concatenate(df['values'].values),
        "lines": [item for sublist in df['lines'].values for item in sublist],
    })
    return df_expanded


def token_frequencies(tokens, normalize=False):
    df = tokens.groupby(["type", "value"]).size().reset_index(name="num")
    num_tokens = len(tokens)
    if normalize:
        df['num'] = df['num'].apply(lambda x: x / (1.0 * num_tokens))
    return df.sort_values(by=['num'], ascending=False)


def get_token_freq(df):
    df_expanded = expand_df_tokens(df)
    freq = token_frequencies(df_expanded, normalize=False)
    return freq
