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

   * Each key bit keeps track of which Blocks it is used in

   * Implement basic Binary algorithm

   * Implement basic Cascade algorithm

   * Implement Cascade variations

     * Deterministic shuffle

     * Discard corrected bits?

   * Replicate Andre Reis Cascade study to make sure that my implementation is sane

   * Restructure controlled seeding of random function (will affect test cases).

   * Code coverage on codecov should also include bb84 module itself.

   * Indent Google docstrings with more than one parameter.
