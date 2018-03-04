import json
import os
import tempfile
import shutil
import argparse

# from scoring_tool.scoring_tool import get_project_score, load_setup_args
import scoring_tool.scoring_tool as scoring
# from scoring_tool.scoring_tool import get_project_score


def write_src_data(data_path, json_data, project_class, project_name, verbose=False):
    out_path = os.path.join(data_path, project_class)
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    out_path = os.path.join(out_path, project_name)
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    for f in json_data:
        filename_with_roots = f["fullPath"]
        roots = filename_with_roots.split("/")[:-1]
        if len(roots) > 0:
            root_path = out_path
            for root in roots:
                root_path = os.path.join(root_path, root)
                if not os.path.exists(root_path):
                    os.mkdir(root_path)
        with open(os.path.join(out_path, filename_with_roots), 'w') as f_out:
            f_out.write(f["data"])

    if verbose:
        # test
        print("Filesystem: ")
        test_filesys(data_path)


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def data_from_payload(json_payload, verbose=False):
    if verbose:
        print("Payload: ")
        for key, value in json_payload.items():
            print(key, value)
    project_category = json_payload["category"]
    project_name = json_payload["dAppName"]
    json_data = json_payload["files"]
    if verbose:
        print("Data: ")
        for f in json_data:
            print(f)
    return json_data, project_category, project_name


def test_filesys(tmp_path):
    # print
    list_files(tmp_path)
    for path, dirs, files in os.walk(tmp_path):
        print path
        for f in files:
            print f
            file_path = os.path.join(os.path.join(tmp_path, path), f)
            with open(file_path, 'r') as f_in:
                lines = f_in.readlines()
                print lines


def payload2score(setup_args, json_payload, use_tmp_dir=True):
    if use_tmp_dir:
        # make dir
        tmp_path = tempfile.mkdtemp()
        # overwrite setup args
        setup_args["data_path"] = tmp_path
        setup_args["out_path"] = os.path.join(tmp_path, "out")

    json_data, project_class, project_name = data_from_payload(json_payload, setup_args["verbose"])

    write_src_data(setup_args["data_path"], json_data, project_class, project_name, setup_args["verbose"])

    # RUN
    score, metrics = scoring.get_project_score(setup_args, project_class, project_name)

    if use_tmp_dir:
        shutil.rmtree(tmp_path)

    return score, metrics


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup_path", type=str, default='scoring_tool/setup',
        help="path of setup JSONs, containing setup.json, weights.json, categoric_norm.json, numeric_norm.json",
    )
    parser.add_argument(
        "--payload_file", type=str, default='web_integration/payload.json',
        help="filename of payload JSON",
    )
    args = parser.parse_args()
    return args


def main():
    # Note:
    # The following files need to exist:
    # setup_path: path containing setup.json, weights.json, categoric_norm.json, numeric_norm.json
    # (in setup.json) zeppelin_path: path containing /Zeppelin/Zeppelin/<Zeppelin repo>
    # payload_file: path and filename of JSON payload

    # setup
    args = parse_args()
    setup_args = scoring.load_setup_args(setup_path=args.setup_path)

    # payload
    with open(args.payload_file, 'r') as f:
        json_payload = json.load(f)

    # RUN
    score, metrics = payload2score(setup_args, json_payload)


if __name__ == '__main__':
    main()
