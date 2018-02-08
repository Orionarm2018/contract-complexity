
import pandas as pd


def analyse_dataset(df_files):
    # how often is zeppelin imported?

    imports_z = df_files.groupby(['class', 'company'])['imports_zeppelin'].sum()
    # contains_z = df_files.groupby(['class', 'company'])['contains_zeppelin'].sum()
    z_presence = pd.DataFrame(pd.Series(imports_z))
    # z_presence['contains_zeppelin'] = contains_z

    print(z_presence)
