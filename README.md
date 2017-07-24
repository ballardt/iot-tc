Feature Extraction
==================

Daily Features
--------------

To extract the workshop paper features for each device over each date using the scripts in this repo:

1. Download and extract the dataset (found [here](http://149.171.189.1/)) into a single folder. There should be one folder filled with 20 pcap files, where each file corresponds to all of the traffic for one day.

2. Run `split-dates.sh`:
    ```
    ./split-dates.sh path/to/dataset/folder path/to/output/folder
    ```
    Note that the output files will **not** be placed directly into the specified output folder. They will be placed in `path/to/output/folder/split-dates/`

3. Run `extract.sh`:
    ```
    ./extract.sh path/to/split-dates/folder path/to/output/file/folder
    ```
    Note that the `path/to/split-dates/folder` should **include** `split-dates`. For example, after running step 2., I may run `./extract.sh ~/split-dates ~/`. Also note that a single file, `split-dates-features.csv`, is placed into the specified output folder. `split-dates-features.csv` has the extracted features.


Hourly Features
---------------

Exactly like the daily features, but the filenames are `split-hours.sh` and `extract-hours.sh`, and "dates" is changed to "hours" elsewhere:

1. Download and extract the dataset (found [here](http://149.171.189.1/)) into a single folder. There should be one folder filled with 20 pcap files, where each file corresponds to all of the traffic for one day.

2. Run `split-hours.sh`:
    ```
    ./split-hours.sh path/to/dataset/folder path/to/output/folder
    ```
    Note that the output files will **not** be placed directly into the specified output folder. They will be placed in `path/to/output/folder/split-hours/`

3. Run `extract-hours.sh`:
    ```
    ./extract-hours.sh path/to/split-hours/folder path/to/output/file/folder
    ```
    Note that the `path/to/split-hours/folder` should **include** `split-hours`. For example, after running step 2., I may run `./extract-hours.sh ~/split-hours ~/`. Also note that a single file, `split-hours-features.csv`, is placed into the specified output folder. `split-hours-features.csv` has the extracted features.
