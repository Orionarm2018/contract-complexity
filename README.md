# Code Complexity Estimator for Smart Contracts
Author: Oskar Triebe, February 2018

## Purpose
This is a scoring tool to estimate the complexity of a project based on its source code.
It is designed for smart contracts based on Solidity. However, it could easily be repurposed for Python or other languages.

## Use
High-level overview:
Given a path to a the source code filesystem, the scoring tool computes a complexity score in the range of [0, 1].

### Call Scorer (Python)
Call `get_project_score` from `scoring_tool/scoring_tool.py` with arguments:
```python
get_project_score(
    setup_args, 
    project_class, 
    project_name,
)
```
With `setup_args = setup_args = load_setup_args(setup_path)` being a dict with setup arguments loaded from `setup_path` containing `setup.json, weights.json, categoric_norm.json, numeric_norm.json`. 
For an example, see `scoring_tool/setup/`.


### Call Scorer (Commandline)
Call `scoring_tool/scoring_tool.py --setup_path <path_to_setup_files>`. 
For details on `setup_path`, see above or see implementation in `main()` for example.

### Call Scorer with JSON payload (Python)
Call `payload2score` from `scoring_tool/web_integration.py` with arguments:

```python
payload2score(
    setup_args, 
    json_payload, 
    use_tmp_dir,
)
```
This is a wrapper around `get_project_score`, which creates a temporary filesystem from the project data contained in the JSON payload.

### Call Scorer with JSON payload ((Commandline)
Just like above, call `web_integration/payload2score.py --setup_path <path_to_setup_files> --payload_file <payload_file>` . 
Additionally supply `payload_file`: path and filename of JSON payload.


## Notes
Filesystem assumes the structure `<data_path>/<project_class>/<project_name>/<nested repo with src files>`

