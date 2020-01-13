************
Reflections.
************

Reflections on the Cascade-python code.
=======================================

To be honest, in retrospect I am not entirely happy about the code that I ended up with. The reason I am not happy with the code is that it turned out to be too complex and too slow. Also, the code made some simplistic assumptions that will not be satisfied in any real product. I will elaborate on each of these points.

I made several attempts to improve the code (see branches failed-improvement-attempt-1 and-2 in the GitHub repository) but in each case I ended up with something that was even more complex and even slower. I will also elaborate on what I tried and why it failed.

Before we get into the details of what went wrong and what could be improved, I can already say that the root cause of my problems is my old nemesis "premature optimization". Right from the get-go, I assumed that certain operations (e.g. recomputing a parity over a large block of bits in a shuffled key) were going to be expensive, and I introduced all sorts of complex data structures and algorithms to avoid those expensive operations. Those optimizations made the code fragile and slow. I would have been better off keeping things simple.

I have come to the realization that I will need to do a complete rewrite of the code, but I have not decided yet whether I will do a rewrite in Python or whether I will jump directly to C or C++ or Rust (see @@@ for details on why I need to jump to another language anyway for reasons unrelated to performance).

Shuffling keys

One of the key steps in Cascade is to shuffle a key, i.e. to re-order the bits in a key in a random fashion. These keys can be very large: tens of thousands or even hundreds of thousands of bits.

Cascade shuffles the key only once per iteration. Keep in mind that there are not many iterations in Cascade: between 2 and 10 or so, depending on the variation of Cascade. 

Key bit mappings

When Cascade shuffles a key, it needs to remember the mapping between a bit in the shuffled key to the corresponding bit in the original unshuffled key and vice versa.

This mapping is needed because when Cascade flips a bit in the key to correct and error, it needs to find the cascaded blocks that are affected by that bit-flip. Those cascaded blocks were created in different iterations using different key shuffles.

To make this a bit more clear, consider the following example.