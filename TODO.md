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

 * Progress on Cascade implementation (information reconciliation):

   * Implement basic Cascade algorithm

   * Implement Cascade variations

     * Deterministic shuffle

     * Discard corrected bits? At the end?

     * Implement BICONF

     * Did I unwittingly implement Block Reuse without knowing it? Original only uses top-level blocks?

     * Only register error blocks from previous iterations than the block which is being corrected.

     * Support different number of iterations and values for k[i].

   * Finish the Cascade protocol by supporting multiple iterations.

   * Replicate Andre Reis Cascade study to make sure that my implementation is sane.

   * Code coverage on codecov should also include bb84 module itself.

   * Move cascade module one directory up (make it a peer module of bb84).

   * Move the isolated random number generators to the Session object.

   * Add lots of statistics to the Cascade algorithm

   * Automate running multiple iterations of same scenario

   * Automate running multiple scenarios

   * Use all available cores using multi-threading

   * Move ask_correct_parity_function to Session constructor

   * Add statistics

   * Further optimize code based on profiling results

   * Option to only put top-level blocks in map (no sub-block re-use)
