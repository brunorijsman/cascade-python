*****************
The Shuffle class
*****************

A Shuffle object represents a specific permutation (i.e. re-ordering) of key bits.

TODO: Add more detail here.


TODO: Provide examples.

Shuffle identifier
##################

The concept of a shuffle identifier is used when Bob asks Alice to compute the correct parity for some subset of the bits in a shuffled key. Because the keys are large, this subset over which Alice must compute the correct parity can contain a very large number of bits. And while the subset of bits is a contiguous range in the shuffled key, it is not a contiguous range of bits in the original unshuffled key. For example, if the key size is 10,000 bits, Bob might want Alice to compute the correct parity over some random subset of 5,000 bits in the original unshuffled key.

Bob could send a message to Alice that explicitly lists all 5,000 key bit indexes for which Alice should compute the correct parity. But that would be extremely costly and inefficient: these messages would be very large, and Bob will be sending many of these messages.

Instead, Bob uses another more efficient approach based on the shuffle identifiers. Instead of explicitly sending a large number (5,000 in our previous example) of key indexes, Bob sends the following:

    * The identifier of the Shuffle object that Bob used to shuffle the key.

    * The start_shuffle_index and the end_shuffle_index that identifies the contiguous subset of bits in the shuffled key over which Alice must compute the parity.

    * Thus, instead of sending a very large message with thousands of indexes, Bob sends a small message with only three numbers (the shuffle_identifier, the start_shuffle_index, and the end_shuffle_index).

When Alice receives this message from Bob, she can calculate the correct parity as follows:

    * Alice constructs a Shuffle object from the shuffle_identifier that she received from Bob. This Shuffle object is guaranteed to shuffle the key in exactly the same way as the Shuffle object that Bob used (i.e. guaranteed to create the exact same permutation of key bits).

    * Construction a Shuffle object from a shuffle_identifier is still a somewhat expensive operation (linear in the size of the key, in both space and time). However, Bob will only use a very limited number of Shuffle objects, namely one Shuffle object per iteration in the Cascade algorithm (i.e. typically between 4 and 14 Shuffle objects, depending on the exact variation of the Cascade algorithm). Thus, Alice will only see a small number of unique shuffle_identifier values and she can create a cache of Shuffle objects, indexed by the shuffle_identifier.

    * Once Alice has created the Shuffle object (based on the shuffle_identifier) she can re-create the shuffled key that Bob used, and compute the correct parity over what is now a contiguous range of bits start_shuffled_index ... end_shuffled_index.

The concept of a shuffle_identifier is only intended to make the protocol more efficient. It has nothing to do with security. Specifically, it is assumed that Eve, the eavesdropper, can observe the shuffle_identifier can re-create the Shuffle object (i.e. the permutation of key bits) from it.

Shuffle random number generators
################################

The Shuffle module uses a rather complex arrangement with multiple separate and isolated random number generators. This complex arrangement exists for two reasons:

    1. To enable a shuffle object to be re-created using only the shuffle identifier, and end up
       with a new shuffle object that generates the exact same permutation of key bits (as
       described above).

    2. To enable the unit tests to be deterministic: when we run the same unit test multiple times,
       the exact same sequence of random shuffle objects is created.

TODO: Continue from here.

You might wonder whether this arrangement still works when multiple different version of Python are involved, for example:

    1. Bob creates a shuffle object.

    2. Bob sends the identifier of the shuffle object to Alice.

    3. Alice re-creates the shuffle object using the shuffle identifier received from Bob.

The question is: will this still work fine if Alice and Bob are running different versions of Python? The concern is that the random number generators in the different versions of Python generate different random number sequences for the same seed. If that were to happen, then Alice's shuffle object would permute keys in a different way than Bob's shuffle object.

We need not be concerned. It *does* work fine because the Python documentation for the random module says the following: "Most of the random module’s algorithms and seeding functions are subject to change across Python versions, but two aspects are guaranteed not to change: If a new seeding method is added, then a backward compatible seeder will be offered. The generator’s random()method will continue to produce the same sequence when the compatible seeder is given the same seed."
