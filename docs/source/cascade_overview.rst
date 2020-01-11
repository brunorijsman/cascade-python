************************************************************
Overview of the Cascade information reconciliation protocol.
************************************************************

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

Parallelization.
================

Variations on the Cascade Protocol.
===================================

Variations on the Cascade Protocol.
===================================













