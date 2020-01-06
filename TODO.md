* Implement Cascade variations:

  * Deterministic shuffle.

  * Discard corrected bits at the end.

  * BICONF.

  * Different number of iterations and values for k[i].
  
  * Full Block Parity Inference (BPI).

* run_experiments:

  * Add command-line for output file and flush after each result

  * Report progress to stdout

* Reproduce Andre Reis Cascade thesis stats.

* Reproduce "Demystifying the Information Reconciliation Protocol Cascade" paper stats.

* Move cascade module into a separate Git repo and make it a dependency for the bb84 repo.

* Add more statistics to the Cascade algorithm:

  * Actual seed value.

  * Efficiency.

* Add or move configuration items into parameters block:

  * Request seed value.

* Separate JSON objects for experiment and data_point.

* Automate running multiple scenarios.

* Use all available cores using multi-threading.

* Further optimize code based on profiling stats.

* Use type annotations instead of asserts.

* Reserved shuffle ID zero = no shuffling?

* Get test coverage back to 100%.

* Get documentation back to 100%.

* Automatically produce stats graph.

* Script to only reproduce missing stats (based on parameters)

* Optionally regenerate stats when version code has changes.

* Put LaTeX document that includes generated graphs under version control.

* Publish cascade in Pip.

* Make cascade a Pip dependency for BB84.

* Make Spinx only document the public classes (and not the internal classes).

* Allow key_size to be a range (similar to error_rate)

* Better --help documentation for error_rate (it can be a value or a range)

* Cover study scripts with unit tests.

* Cover study with lint.

* Don't repeat the shuffle index so often in ask_parities message (it makes the efficiency much worse).