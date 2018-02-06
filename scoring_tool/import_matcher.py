
from utils import flatten


def import_contains_inherited_contract(import_match, inherited_contracts):
    import_match_contracts = flatten(import_match['contract_name'])
    inherited_contracts = flatten(flatten(inherited_contracts))
    # is_contained = [x in import_match_contracts for x in inherited_contracts]
    # is_contained = any(is_contained)
    imported_contracts_also_inherited = set(import_match_contracts).intersection(inherited_contracts)
    is_contained = len(imported_contracts_also_inherited) > 0
    return is_contained


def match_imports_with_files(df_files, files_zeppelin, verbose=False):
    # WIP
    # match imported files with files in dataset
    df_files['ID'] = df_files.index.values
    df_files['imports_idx'] = None
    df_files['imports_zeppelin'] = False
    # df_files['contains_zeppelin'] = False

    # TODO: add these two, combine files based on inheritance instead of imports
    # NOTE: is done instead by setting import idxs to -3 if not inherited
    # df_files['inherits_idx'] = None
    # df_files['is_inherited'] = False

    # only import file if it contains an inherited contract!
    import_only_inherited = True

    # allow imports from zeppelin
    allow_zeppelin = True

    for idx in df_files.index.values:
        f = df_files.loc[idx]
        #     df_files.loc[idx, 'contains_zeppelin'] = 'zeppelin' in f.loc['src'].lower()
        company = f.loc['company']
        files_company = df_files[df_files['company'] == company]
        f_imports = f.loc['imports']
        f_imports_path = f.loc['imports_path']
        f_inherited = flatten(f.loc['inherited_contracts'])

        #     if len(f_imports) < 1:
        #         continue
        imports_idx_list = []
        for import_file_name, import_file_path in zip(f_imports, f_imports_path):
            matching_files = files_company[files_company['file_name'] == import_file_name]

            # check if is importing from zeppelin, as these often in other folder
            if 'zeppelin' in import_file_path.lower():
                df_files.at[idx, 'imports_zeppelin'] = True
                if allow_zeppelin and company.lower() != 'zeppelin':
                    matching_files = matching_files.append(
                        files_zeppelin[files_zeppelin['file_name'] == import_file_name])

            if len(matching_files) == 1:
                imports_idx = matching_files.index.values[0]

            elif len(matching_files) > 1:
                # handle ties
                target_set = set(import_file_path.split('/'))
                num_joint_roots = []
                for match_root in matching_files['root'].values:
                    joint_roots = [1 for r in match_root.split('/') if r in target_set]
                    num_joint_roots.append(sum(joint_roots))
                max_matches = max(num_joint_roots)
                if sum(max_matches == m for m in num_joint_roots) > 1:
                    # handle tie-tie
                    root_len_diff = [abs(len(import_file_path.split('/')) - len(r.split('/')))
                                     for r in matching_files['root'].values]
                    better_match = root_len_diff.index(min(root_len_diff))
                else:
                    better_match = num_joint_roots.index(max_matches)
                imports_idx = matching_files.index.values[better_match]

                if verbose:
                    print "import root: {}; matching roots: {}".format(import_file_path, matching_files['root'].values)
                    print "has match: ", import_file_path in matching_files['root'].values

            elif len(matching_files) < 1:
                imports_idx = -1
                if verbose:
                    print "no import match for: ", import_file_name, import_file_path

            # check if the import-match also contains an inherited contract
            if import_only_inherited and imports_idx >= 0:
                if not import_contains_inherited_contract(df_files.loc[imports_idx], f_inherited):
                    if verbose:
                        print "import: ", df_files.loc[imports_idx][
                            'contract_name'], "not contain inherited contract: ", f_inherited
                    imports_idx = -3

            imports_idx_list.append(imports_idx)

        df_files.at[idx, 'imports_idx'] = imports_idx_list

