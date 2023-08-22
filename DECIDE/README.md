# Usage

Please refer to [Requirements.md](../Requirements.md) and [Installation.md](../Installation.md).

To detect version incompatibility issues in a given deep learning project, one can create a folder named by the project's name in `DECIDE/benchmark` and follows the format of files in `DECIDE/benchmark/examples` to specify the project-required libraries and the local stack information. Then run:

```shell
$ python main.py -n PROJ_NAME
```

Parameters:

- `-n`: the name of detect project.
- `-m`: the mode of collecting information in local stack. Use 'file' to collect from `DECIDE/benchmark/PROJ_NAME/local_info.json`, use 'local' to directly gather the version information by scanning the local machine.
- `-l` (Optional): the specified file path of local stack information, default path is `DECIDE/benchmark/PROJ_NAME/local_info.json` .
- `-r` (Optional): the specified file path of version information of libraries required by the project, default path is `DECIDE/benchmark/PROJ_NAME/requirements.txt`.
- `-p` (Optional): The root path of the target project.

## Replay Experiments

To replay the evaluation in our benchmark, please run:

```shell
$ chmod +x experiment.sh
$ ./experiment.sh
```

The results will be generated in `DECIDE/detection_result`.