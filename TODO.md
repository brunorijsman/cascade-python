* Implement Cascade variations:

  * Discard corrected bits at the end.

  * Option (5) in Demystifying paper (deterministic shuffle)

  * Option (6) in Demystifying paper (remove singleton blocks)

  * Full Block Parity Inference (BPI).

* Better handling of error_rate 0.0 for efficiency (don't assume 1.0, instead skip in graph)

* run_experiments:

  * Have nr_runs and error_rate_resolution as parameters for the script

* graph

  * Option to write to file

  * Higher resolution near error_rate 0.0

* Reproduce Andre Reis Cascade thesis stats.

* Reproduce "Demystifying the Information Reconciliation Protocol Cascade" paper stats.

* Move cascade module into a separate Git repo and make it a dependency for the bb84 repo.

* Make results reproducible:

  * Report actual seed value.

  * Allow seed value to be specified (to reproduce)

* Further optimize code based on profiling stats.

* Add unit tests for study scripts.

* Add implementation documentations.

* Add results documentations.

* Publish cascade in Pip.

* Make cascade a Pip dependency for BB84.

* Make Spinx only document the public classes (and not the internal classes).

* Better --help documentation for error_rate (it can be a value or a range)

* Don't repeat the shuffle index so often in ask_parities message (it makes the efficiency much worse).
