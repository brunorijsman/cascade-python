# BB84

  * Am I using the correct CQC-Python library? https://github.com/SoftwareQuTech/CQC-Python vs https://github.com/SoftwareQuTech/SimulaQron

  * Use SimulaQron from GitHub source instead of pip install

  * File SimulaQron enhancement request: report sender when receiving message

  * File SimulaQron enhancement request: wait for any event (qubit or classical message or timeout)

  * File SimulaQron enhancement request: asynchronous model (or is there already a low-level API for this)?

  * Add authentication and data integrity on classical channel (see http://bit.ly/bb84auth)

  * Add documentation comments (bb84 module; cascade already done)

  * Add noise estimation

  * Add privacy amplification

  * Keep stats for measured qubits

  * Report Alice and Bob key, and differences at end of run

  * Handle case that block size is not multiple of window size

  * Rename bb84 block to something else

  * Get rid of report kwargs, instead make report public

  * Populate README.md file

  * Introduce "Evan" who does a full man-in-the-middle attack

  * Introduce a middle node for modeling normal (non-attack) noise

  * Code coverage on codecov should also include bb84 module itself.

# Cascade

  * Implement Cascade variations

    * Deterministic shuffle.

    * Discard corrected bits at the end.

    * BICONF

    * Different number of iterations and values for k[i].
    
    * Full Block Parity Inference (BPI).

  * Reproduce Andre Reis Cascade thesis results.

  * Reproduce "Demystifying the Information Reconciliation Protocol Cascade" paper results.

  * Move cascade module into a separate Git repo and make it a dependency for the bb84 repo.

  * Add more statistics to the Cascade algorithm:

    * Reconciliation run-time.

    * Git version of code.

    * Actual seed value.

  * Add or move configuration items into parameters block:

    * Name of block size function.

    * Request seed value.

    * Key size.

    * Fixed error count / Bernoulli error rate.

  * Automate running multiple iterations of same scenario.

  * Automate running multiple scenarios.

  * Use all available cores using multi-threading.

  * Further optimize code based on profiling results

  * Reserved shuffle ID zero = no shuffling?

  * Get test coverage back to 100%.

  * Get documentation back to 100%.

  * Automatically produce results graph.

  * Script to only reproduce missing results (based on parameters)

  * Optionally regenerate results when version code has changes.

  * Put LaTeX document that includes generated graphs under version control.
