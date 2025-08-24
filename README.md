# Accountant

My personal accounting software.

## Usage

### Requirements
Tested with Python 3.11.12, with the packages listed in `requirements.txt`.

### How to use
Define a specification file (see `example/spec_example.yaml` for an example).

Define a categorization file describing how you would classify different expenses (see `example/categorization_example.yaml`).  Categorizations can be based on keywords in the expense description, or on the entire exact expense description. Add this categorization to your specification file.

Put your data in directories in this format:
```bash
- <year 1>
    - <data source 1>
    - <data source 2>
    - <...>
- <year 2>
    - <data source 1>
    - <data source 3>
    - <...>
- <...>
```

Define functions which turn files into a standard format of data in `accounting/normalize_funcs.py`. The standard format is defined in `accounting.transaction_file.py`.

Run the report generation script. For example:
```python
./generate_reports.py example/spec_example.yaml
```

Look where the script output says it writes its results. 

Don't forget to delete the cache (`path_data_normalized` in the specification file) if you change the data file contents.


## TODO
- Logging
- Validate entries with more than one source against each other before dropping

