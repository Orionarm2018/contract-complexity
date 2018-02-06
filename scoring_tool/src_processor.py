# imports
import os
# import io
import re
# import tokenize
# import json
# import numpy as np
import pandas as pd
# import stringdist

from reader_writer import get_filename_for_row, get_file_src, get_file_comments
from utils import analyse_col_freq, flatten


def analyse_src_contracts(df_files, verbose=False, save_path=None):
    # helper functions:
    def match_all_contracts_from_src_string(src_string):
        regex = "contract .*{\n"
        matches = re.findall(regex, src_string)
        contract_names = []
        inherited_contracts = []
        for match in matches:
            match = match[len("contract "):-len("{\n")]
            match_type = match.split(' is ')
            contract_names.append(match_type[0].strip())
            if len(match_type) > 1:
                inherited_contracts.append([x.strip() for x in match_type[1].split(',')])
            else:
                inherited_contracts.append([])
        return contract_names, inherited_contracts

    def match_contract_name_from_src_string(src_string):
        return match_all_contracts_from_src_string(src_string)[0]

    def match_inherited_contracts_from_src_string(src_string):
        return match_all_contracts_from_src_string(src_string)[1]

    # execution
    df_files['contract_name'] = df_files['src'].apply(
        match_contract_name_from_src_string)
    df_files['inherited_contracts'] = df_files['src'].apply(
        match_inherited_contracts_from_src_string)

    if verbose:
        # check number of files without contract
        len_df = len(df_files)
        files_without_contracts = df_files[df_files['contract_name'].apply(lambda x: len(x) == 0)]
        print "files without contract: ", len(files_without_contracts)
        files_with_contracts = df_files[df_files['contract_name'].apply(lambda x: len(x) > 0)]
        print "files with contract: ", len(files_with_contracts)

        # check files many inherited contracts
        for i in [0, 1]:
            files_with_many_inherited_contracts = files_with_contracts[
                files_with_contracts['inherited_contracts'].apply(lambda x: len(flatten(x)) == i)]
            print "files with {} inherited contracts: {}/{}".format(i, len(files_with_many_inherited_contracts), len_df)
        for i in [2, 5]:
            files_with_many_inherited_contracts = files_with_contracts[
                files_with_contracts['inherited_contracts'].apply(lambda x: len(flatten(x)) >= i)]
            print "files with {} or more inherited contracts: {}/{}".format(i, len(files_with_many_inherited_contracts), len_df)

    if verbose or save_path is not None:
        # compute frequency of inherited files
        inheritance_flat = flatten(flatten(df_files['inherited_contracts']))
        col_counts = pd.Series(inheritance_flat).value_counts(sort=True)
        if save_path is not None:
            col_counts.to_csv(os.path.join(save_path, 'counts_{}.csv'.format('inheritance')))
        if verbose:
            print "inheritance counts: ", col_counts

    return df_files


def analyse_src_imports(df_files, verbose=False, save_path=None):
    # helper functions:
    def match_imports_from_src_string(src_string):
        # retrieve imports including path
        regex = "import .*;\n"
        matches = re.findall(regex, src_string)
        matches_cleaned = [m[len("import '"):-len("';\n")] for m in matches]
        return matches_cleaned

    def exctract_imports(src_string):
        # retrieve imports
        matches_cleaned = match_imports_from_src_string(src_string)
        imports = [m.split('/')[-1] for m in matches_cleaned]
        return imports

    def exctract_imports_path(src_string):
        # retrieve imports paths
        matches_cleaned = match_imports_from_src_string(src_string)
        imports_path = []
        for m in matches_cleaned:
            cleaned_imports_path = [x for x in m.split('/')[:-1] if x not in [".", "..", " ", ""]]
            imports_path.append("/".join(cleaned_imports_path))
        return imports_path

    # execution
    df_files['imports'] = df_files['src'].apply(exctract_imports)
    df_files['imports_path'] = df_files['src'].apply(exctract_imports_path)

    if verbose:
        # check files with (many) imports
        len_df = len(df_files)
        for i in [0, 1]:
            files_with_imports = df_files[df_files['imports'].apply(lambda x: len(x) == i)]
            print "files with {} imports: {}/{}".format(i, len(files_with_imports), len_df)
        for i in [1, 5]:
            files_with_imports = df_files[df_files['imports'].apply(lambda x: len(x) >= i)]
            print "files with {} or more imports: {}/{}".format(i, len(files_with_imports), len_df)

    if verbose or save_path is not None:
        # compute frequency of imports files
        imports_flat = flatten(df_files['imports'])
        col_counts = pd.Series(imports_flat).value_counts(sort=True)
        if save_path is not None:
            col_counts.to_csv(os.path.join(save_path, 'counts_{}.csv'.format('imports')))
        if verbose:
            print "imports counts: ", col_counts

    return df_files


def run_analysis():
    # NOTE: Has bugs re-reading df from csv, as empty fields are NaNs
    # currently not relevant as we plan to keep all in memory,
    # but needs to be fixed if reading from csv
    print "hello, what are you looking for?\n This tool might be bugged"

    # DATA_PATH = '/home/ourownstory/Documents/SOL/derived/'
    OUT_PATH = '/home/ourownstory/Documents/SOL/derived/'
    data_path = OUT_PATH + 'cleaned/'

    df = pd.read_csv(OUT_PATH + 'df_files.csv', na_values=[])
    df.fillna('')

    _ = analyse_col_freq(df, out_path=OUT_PATH, save_csv=True)
    # print _

    df = df.apply(get_file_src, axis=1, args=(data_path, True))



if __name__ == '__main__':
    run_analysis()
