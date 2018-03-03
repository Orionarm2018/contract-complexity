import json
import os
import tempfile
import shutil

from scoring_tool.scoring_tool import get_project_score, load_setup_args


def write_src_data(data_path, json_data, project_class, project_name):
    out_path = os.path.join(data_path, project_class)
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    out_path = os.path.join(out_path, project_name)
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    for f in json_data:
        filename_with_roots = f["fullPath"]
        roots = filename_with_roots.split("/")[:-1]
        filename = filename_with_roots.split("/")[-1]
        if len(roots) > 0:
            root_path = out_path
            for root in roots:
                root_path = os.path.join(root_path, root)
                if not os.path.exists(root_path):
                    os.mkdir(root_path)
        with open(os.path.join(out_path, filename_with_roots), 'w') as f_out:
            f_out.write(f["data"])


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def data_from_payload(json_payload):
    json_data = json_payload["files"]
    return json_data


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


def main():
    # TODO: fix bug with included Zeppelin files -> provide separate path
    with open('payload.json', 'r') as f:
        json_payload = json.load(f)

    json_data = data_from_payload(json_payload)
    for f in json_data:
        print(f)

    tmp_path = tempfile.mkdtemp()

    project_class = 'UNK'
    project_name = 'X'
    write_src_data(tmp_path, json_data, project_class, project_name)

    # test
    test_filesys(tmp_path)

    # setup
    setup_path = '../scoring_tool/setup'
    setup_args = setup_args = load_setup_args(setup_path)
    setup_args["data_path"] = tmp_path
    setup_args["out_path"] = os.path.join(tmp_path, "out")
    setup_args["save_results"] = False

    # RUN single
    print(get_project_score(setup_args, project_class, project_name))

    shutil.rmtree(tmp_path)


if __name__ == '__main__':
    main()
