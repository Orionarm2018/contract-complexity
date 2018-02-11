import pandas as pd

from utils import flatten
from src_processor import remove_import_lines


def import_contains_inherited_contract(import_match, inherited_contracts, verbose=False):
    import_match_contracts = import_match['contract_name']
    inherited_contracts = flatten(flatten(inherited_contracts))
    # is_contained = [x in import_match_contracts for x in inherited_contracts]
    # is_contained = any(is_contained)
    imported_contracts_also_inherited = set(import_match_contracts).intersection(inherited_contracts)
    is_contained = len(imported_contracts_also_inherited) > 0
    if verbose and is_contained:
        print("imported file contains inherited contracts: {}".format(imported_contracts_also_inherited))
    return is_contained


def match_imports_with_files(df_files, files_zeppelin=None, import_only_inherited=True, verbose=False):
    # only import file if it contains an inherited contract!

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

    # allow imports from zeppelin
    allow_zeppelin = files_zeppelin is not None

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
            this_import_is_from_zeppelin = False

            # check if is importing from zeppelin, as these often in other folder
            if 'zeppelin' in import_file_path.lower() and len(matching_files) == 0:
                df_files.at[idx, 'imports_zeppelin'] = True
                if allow_zeppelin and company.lower() != 'zeppelin':
                    matching_files = matching_files.append(
                        files_zeppelin[files_zeppelin['file_name'] == import_file_name])
                    this_import_is_from_zeppelin = True

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

            elif len(matching_files) == 0:
                imports_idx = -1
                if verbose:
                    print "no import match for: ", import_file_name, import_file_path

            # check if the import-match also contains an inherited contract
            if import_only_inherited and imports_idx >= 0:
                if this_import_is_from_zeppelin:
                    import_match = files_zeppelin.loc[imports_idx]
                else:
                    import_match = df_files.loc[imports_idx]
                if not import_contains_inherited_contract(
                        import_match=import_match, inherited_contracts=f_inherited, verbose=verbose):
                    if verbose:
                        print "imported contract: ", import_match['contract_name'], \
                            "does not contain inherited contract: ", f_inherited
                    imports_idx = -3

            imports_idx_list.append(imports_idx)

        df_files.at[idx, 'imports_idx'] = imports_idx_list

    # check if is imported
    imported_idxs = set(flatten(df_files['imports_idx'].values))
    df_files['is_imported'] = df_files['ID'].apply(lambda x: x in imported_idxs)

    return df_files


def get_all_imports_idx_and_depth(df, imports_idx, idx_set, depth_list, depth, max_depth):
    #     print 'imports_idx: ', imports_idx
    #     print 'idx_set: ', idx_set
    #     print 'depth: ', depth
    #     print 'depth_list: ', depth_list
    depth += 1
    if depth <= max_depth:
        for idx in imports_idx:
            # print 'idx: ', idx
            if idx not in idx_set:
                idx_set.add(idx)
                depth_list.append(depth)
                if idx >= 0:
                    next_imports_idx = df.loc[idx, 'imports_idx']
                    if len(next_imports_idx) > 0:
                        # print 'next_imports_idx: ', next_imports_idx
                        _, _ = get_all_imports_idx_and_depth(df, next_imports_idx, idx_set, depth_list, depth, max_depth)

    else:
        print "max_depth reached for :"
        print idx_set
        print depth_list
        # TODO: also import zeppelin files (and their imports)?
        # print 'reached return: ', idx_list
        # print 'depth: ', depth, depth_list
    return idx_set, max(depth_list)


def add_all_imports_idx_and_depth_to_row(row, df, join_all, max_depth):
    idx_set = set([row['ID']])
    depth_list = [0]
    depth = 0
    #     print row
    if join_all or row.loc['is_imported'] == False:
        imports_idx_all, imports_depth = get_all_imports_idx_and_depth(
            df=df,
            imports_idx=row.loc['imports_idx'],
            idx_set=idx_set,
            depth_list=depth_list,
            depth=depth,
            max_depth=max_depth,
        )
        row['imports_idx_all'] = flatten(list(imports_idx_all))
        row['imports_depth'] = imports_depth
    else:
        row['imports_idx_all'] = []
        row['imports_depth'] = -1
    return row


def recurse_imports(df, join_all, max_depth, verbose=False):
    # recursively find imports idxs up to max_depth
    df = df.apply(add_all_imports_idx_and_depth_to_row, axis=1, args=(df, join_all, max_depth))
    return df


def join_imports(row, df_files):
    row.loc['joined_files'] = []
    row.loc['joined_contracts'] = []
    row.loc['joined_roots'] = []
    src_joined = []
    comments_joined = []
    for idx in row.loc['imports_idx_all']:
        if idx >= 0:
            row.loc['joined_files'].append(df_files.loc[idx, 'file_name'])
            row.loc['joined_contracts'].extend(df_files.loc[idx, 'contract_name'])
            row.loc['joined_roots'].extend(df_files.loc[idx, 'root'].split('/'))
            src_joined.append(df_files.loc[idx, 'src'])
            comments_joined.append(df_files.loc[idx, 'comments'])
            if df_files.loc[idx, 'imports_zeppelin']:
                row.loc['imports_zeppelin'] = True
#             if df_files.loc[idx, 'contains_zeppelin'] == True:
#                 row.loc['contains_zeppelin'] = True
    row.loc['joined_src'] = "\n".join(src_joined)
    row.loc['joined_comments'] = "\n".join(comments_joined)
    row.loc['joined_contracts'] = list(set(row.loc['joined_contracts']))
    row.loc['joined_roots'] = list(set(row.loc['joined_roots'] ))
    row.loc['joined_roots'] = [x for x in row.loc['joined_roots'] if x not in ['', '.', '..']]
    del row['imports']
    del row['imports_idx']
    del row['imports_path']
    # del row['inherited_contracts']
#     del row['is_imported']
    return row


def join_imported_files(df_files):
    # remove_import_lines(df_joined.loc[4, 'src'])
    df_files['src'] = df_files['src'].apply(remove_import_lines)
    df_files = df_files.apply(join_imports, axis=1, args=(df_files,))
    return df_files
