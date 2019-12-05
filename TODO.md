 * Add authentication and data integrity on classical channel (see http://bit.ly/bb84auth)

 * Add documentation comments

 * Add type annotations (later, makes the code very less readable)

 * Add noise estimation

 * Add privacy amplification

 * Keep stats for measured qubits

 * Report Alice and Bob key, and differences at end of run

 * Generate documentation

 * Handle case that block size is not multiple of window size

 * Get rid of report kwargs, instead make report public

 * Populate README.md file

 * Introduce "Evan" who does a full man-in-the-middle attack

 * Introduce a middle node for modeling normal (non-attack) noise

 * Move tests directory into module directory of module being tested

 * Start Sphinx documentation

 * Integrate Sphinx documentation into CI/CD workflow (travis and read the docs)

 * Progress on Cascade implementation (information reconciliation):

   * Add unit test cases for Key

   * Each key bit keeps track of which Blocks it is used in

   * Implement Block class

   * Implement basic Cascade algorithm

   * Replicate Andre Reis Cascade study to make sure that my implementation is sane
