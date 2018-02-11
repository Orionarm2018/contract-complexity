
import pandas as pd


def analyse_dataset(df_files):
    # how often is zeppelin imported?

    imports_z = df_files.groupby(['class', 'company'])['imports_zeppelin'].sum()
    # contains_z = df_files.groupby(['class', 'company'])['contains_zeppelin'].sum()
    z_presence = pd.DataFrame(pd.Series(imports_z))
    # z_presence['contains_zeppelin'] = contains_z
    print(z_presence)


def detect_strings(row, strings, case_sensitive=False):
    # detect any list of strings in  ['named', 'contains', 'comments']
    for to_find in strings:
        names_mix = []
        names_mix.extend(row['joined_files'])
        names_mix.extend(row['joined_contracts'])
        names_mix.extend(row['joined_roots'])
        if case_sensitive:
            row['named_{}'.format(to_find)] = any([to_find in x.lower() for x in names_mix])
            row['contains_{}'.format(to_find)] = to_find in row['src'].lower()
            row['comments_{}'.format(to_find)] = to_find in row['comments'].lower()
        else:
            row['named_{}'.format(to_find)] = any([to_find in x for x in names_mix])
            row['contains_{}'.format(to_find)] = to_find in row['src']
            row['comments_{}'.format(to_find)] = to_find in row['comments']
    return row


def detect_crowdsale_presale_ICO(row):
    row = detect_strings(row, strings=['crowdsale', 'presale'])
    return detect_strings(row, strings=['ICO'], case_sensitive=True)


def detect_coin_token(row):
    strings = ['coin', 'token']
    return detect_strings(row, strings)


def count_project_indicators_ICO(df, verbose, add_to_df=True):
    # ICO indicator counts
    indicator_list = ["{}_{}".format(a, b) for a in ['named', 'contains', 'comments'] for b in
                      ['crowdsale', 'presale', 'ICO']]
    if add_to_df:
        df['ICO_indications'] = df[indicator_list].sum(axis=1)
        indicator_list.append('ICO_indications')

    # ICO indicator counts for each company
    ICO_indicators = df.groupby(['class', 'company'])[indicator_list].sum()

    if verbose:
        print ICO_indicators
    return df, ICO_indicators


def count_project_indicators_token(df, verbose, add_to_df=True):
    # Token indicator counts
    indicator_list = ["{}_{}".format(a, b) for a in ['named', 'contains', 'comments'] for b in ['token', 'coin']]
    if add_to_df:
        df['token_indications'] = df[indicator_list].sum(axis=1)
        indicator_list.append('token_indications')

    # Token indicator counts for each company
    token_indicators = df.groupby(['class', 'company'])[indicator_list].sum()

    if verbose:
        print token_indicators
    return df, token_indicators
