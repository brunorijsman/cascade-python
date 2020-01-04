* Implement Cascade variations

  * Deterministic shuffle.

  * Discard corrected bits at the end.

  * BICONF

  * Different number of iterations and values for k[i].
  
  * Full Block Parity Inference (BPI).

* Reproduce Andre Reis Cascade thesis stats.

* Reproduce "Demystifying the Information Reconciliation Protocol Cascade" paper stats.

* Move cascade module into a separate Git repo and make it a dependency for the bb84 repo.

* Add more statistics to the Cascade algorithm:

  * Actual seed value.

* Get rid of start/end_reconciliation_messages stats.

* Add or move configuration items into parameters block:

  * Name of block size function.

  * Request seed value.

  * Key size.

  * Fixed error count / Bernoulli error rate.

* Automate running multiple iterations of same scenario.

* Automate running multiple scenarios.

* Use all available cores using multi-threading.

* Further optimize code based on profiling stats

* Reserved shuffle ID zero = no shuffling?

* Get test coverage back to 100%.

* Get documentation back to 100%.

* Automatically produce stats graph.

* Script to only reproduce missing stats (based on parameters)

* Optionally regenerate stats when version code has changes.

* Put LaTeX document that includes generated graphs under version control.

* Remove cascade code from bb84 (handle as dependency using pip install)

* Make Spinx only document the public classes (and not the internal classes)
