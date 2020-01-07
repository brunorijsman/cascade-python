* Implement Cascade variations:

  * Deterministic shuffle.

  * Discard corrected bits at the end.

  * Full Block Parity Inference (BPI).

* Better handling of error_rate 0.0 for efficiency (don't assume 1.0, instead skip in graph)

* run_experiments:

  * Add command-line for output file and flush after each result

  * Report progress to stdout

  * Use JSON file to control a single experiment

  * Have a script to automate running all experiments and producing all graphs

  * Have nr_runs and error_rate_resolution as parameters for the script

  * Automate running the scripts in AWS instances (including self shut-down and persistence)

  * Write output to configurable file

  * Report progress and estimated finish time to stdout

  * Use all available cores using multi-threading.

  * Mechanism for putting results under version control

* graph

  * Use JSON file to define graph

  * Option to write to file

  * Multiple lines in one graph

  * More general; less hard-coding of graphs

  * Higher resolution near error_rate 0.0

* Reproduce Andre Reis Cascade thesis stats.

* Reproduce "Demystifying the Information Reconciliation Protocol Cascade" paper stats.

* Move cascade module into a separate Git repo and make it a dependency for the bb84 repo.

* Make results reproducible:

  * Report actual seed value.

  * Allow seed value to be specified (to reproduce)

* Separate JSON objects for experiment and data_point.

* Further optimize code based on profiling stats.

* Use type annotations instead of asserts.

* Get test coverage back to 100%.

* Get documentation back to 100%.

* Automatically produce stats graph.

* Put LaTeX document that includes generated graphs under version control.

* Publish cascade in Pip.

* Make cascade a Pip dependency for BB84.

* Make Spinx only document the public classes (and not the internal classes).

* Allow key_size to be a range (similar to error_rate)

* Better --help documentation for error_rate (it can be a value or a range)

* Cover study scripts with unit tests.

* Cover study with lint.

* Don't repeat the shuffle index so often in ask_parities message (it makes the efficiency much worse).

* Rename experiment to data_point

* Use JSON file to control a single graph

