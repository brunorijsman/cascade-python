************************************************
The Cascade information reconciliation protocol.
************************************************

What is an information reconciliation protocol?
===============================================

After Alice and Bob have run a key quantum distribution protocol (QKD) such as BB84, Alice has a "correct key" and Bob has a "noisy key" that is similar but possibly not identical to Alice's correct key.

The QKD protocol provides an estimated Quantum Bit Error Rate (QBER), which is the estimated fraction of bits where Alice's correct key differs from Bob's noisy key. For example if the QBER is 0.01 then 1% of the bits have been flipped.

If the estimated

The BINARY protocol.
====================

Before we explain the Cascade protocol works, we must first explain how the BINARY protocol works.

For blocks with odd numbers of errors, Bob runs the BINARY protocol to perform a dichotomic search to locate and correct exactly one bit error.

The BINARY protocol splits the block into two halves: the left child block and the right child block.

Since the parent block had an odd number of errors, it is certain that either the left child block or the right child block (but not both) has an odd number of errors.

The BINARY protocol recurses into the child block that has an odd number of errors

The Cascade protocol.
=====================


Splitting the key into top-level blocks.
========================================


Multiple iterations and shuffling.
==================================

Consider the following scenario: the Cascade protocol splits the noisy key into blocks and some top-level block contains an even number of errors.

Since Cascade can only correct blocks with an odd number of errors, Cascade will neither detect nor correct any error in that particular block.

How then will the errors in that block get corrected?

Cascade deals with this problem by running multiple iterations (also known as multiple passes). In each iteration:

* Cascade randomly shuffles the bits in the noisy key.

* Cascade splits the shuffled key into new top-level blocks.

By shuffling the noisy key, it is likely (but not certain) that the even number of bit errors that used to be in one block now get spread out over multiple different blocks. And furthermore, it is likely (but once again not certain) that those different blocks end up with only a single bit error.

How likely is it that an even number of errors in one block gets shuffled into an odd number of errors in multiple other blocks? That depends on the bit error rate and on the number of blocks. The higher the bit error rate, the smaller the blocks must be, and hence the higher the number of blocks must be for this to be likely.







Parallelization.
================

In the BINARY protocol, whenever Bob wants to know whether a block contains an even or an odd number of errors, Bob must know the correct parity of the block.

The only way to know the correct parity of the block is to ask Alice:

* Bob must send a message to Alice to ask for the correct parity, and that message must specify for which block the parity is being asked.

* Alice must send a message back to Bob that contains the correct parity.

Each time Bob asks Alice for the correct parity of some block, there is a delay of at least one round trip time (RTT). For example if Alice and Bob are 100 km apart, the delay is at least 1 millisecond considering that the speed of light in fiber is 200,000 km/sec.

Variations on the Cascade Protocol.
===================================

Variations on the Cascade Protocol.
===================================













