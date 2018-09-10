Jump Trading Coding Exercise
-----------------------------

Python 3 is required to run the program. The program was written using version 3.6, but it should work with any
version greater than 3. The program does not use any external dependencies, so a standard distribution will work.

The program was written inside a virtual environment. Run the below command to create one and activate it. Please note
my that local dev machine has versions 2.7 and 3.6, so the Python executable is named python3.

    python3 -m venv jump
    . jump/bin/activate

There is a convenience shell script to run the program within the bin directory.

    ./run.sh ../test_data/jump_test_feed.csv

Use the following commands to run the program without the shell script:

    export PYTHONPATH=.

    python -m jump < test_data/jump_test_feed.csv

In order to run the test suite, execute the following command from with the bin directory:

    ./run_tests.sh