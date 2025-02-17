*******************************************************
Conclusions from Comparison of Results with Literature.
*******************************************************

Here we summarize some of the differences that we observed in the reproduced figures as compared to the literature.

Efficiency.
-----------

I rewrote this section in 2025; it turns out that I had completely misunderstood the concept of Cascade efficiency when I originally wrote the code in 2019/2020.

Originally, I thought that the concept "efficiency" was a measure of how much data was exchanged over the classical channel (i.e. number of messages and size of the messages). The more data was exchanged, the "less efficient" the protocol.

The code estimates the number of bits that were exchanged over the classical channel, and plugs that into a formula (which I did not understand at the time) to compute what the code calls ``realistic_efficiency``. I found that when I plotted this ``realistic_efficiency``, the results did not match the results reported in literature.

I have since come to understand that the concept of "efficiency" in information reconciliation protocols such as Cascade has a very specific meaning.

Every time the Cascade protocol reports a parity bit over the classical channel (which is considered to be authenticated but public), eavesdropper Eve learns one bit of parity information about the secret key. When Eve does a brute force attack, knowing one parity bit value means that she only has to examine half of the possible keys (she can skip the keys with the wrong parity bit).

Thus, for each exposed parity bit, the usable key size is reduced by one bit. If *N* parity bits are exposed in the information reconciliation step, then the privacy amplification step that follows will have to erase *N* bits of leaked information and reduce the final key size by *N* bits.

In information theory it has been proven that the minimum number of exposed bits needed to correct the errors in the produced noisy secret key is:

*n H(ε)* 

where:

*n* is the length of the key,

*ε* is the bit error rate in the key,

*H(ε)* = *-ε* log\ :sub:`2`\ (*ε*) - (1-*ε*) log\ :sub:`2`\ (1-*ε*) is the binary entropy function.

An optimal information reconciliation protocol would achieve this minimum bound.

The efficiency *η* of the Cascade algorithm is then defined as:

*η* = *N* / *n H(ε)*

For example, if the efficiency of Cascade is 1.25 it means that it exposes 25% more parity bits than what an optimal information reconciliation protocol would achieve.

The value *η* is called ``unrealistic_efficiency`` in the code.

Now that I better understand the efficiency calculation, I should update the code to get rid of ``realistic_efficiency`` and rename ``unrealistic_efficiency`` to just ``efficiency``. I did not do that for the Python code in this repository because I did not want to spend another 5 days of running time to reproduce the results. But I did update the C++ implementation in GitHub repository  `cascade-cpp <https://github.com/brunorijsman/cascade-cpp>`_.

Note that the updated C++ code still keeps track of the estimated number of bits that are exchanged over the classical channel. This is interesting for a completely different reason than efficiency: it is relevant to determine how much key material needs to be siphoned off from the produced keys to authenticate the messages on the classical channel.

Less detail.
------------

The graphs in the "demystifying the Information Reconciliation Protocol Cascade” paper are much more detailed because they executed 10,000 (or sometimes even 100,000 or 1,000,000) runs per data point, whereas we only ran 1,000 runs per data point. Our Python implementation was is not fast enough to execute more than 1,000 runs per data point. It already took us about 5 days to run all the experiments on 2xlarge m5 instance on AWS with just 1,000 runs per data point. We are in the process of re-implementing Cascade in C++ which will hopefully allow for more runs per data point.

Standard deviation.
-------------------

The graphs in the original papers do not have any indication of the standard deviation (i.e. no error bars). We have that information for all experiments, although we don't show it in all graphs - we omit it if it would make the graph too noisy.

Differences in the detailed shape of the channel use graph.
-----------------------------------------------------------

In many respects, most of my reproduced channel use figures match the figures in the original literature quite well. The overall shape matches quite well. The numerical value matches quite well. And the appearance of saw-tooth patterns matches quite well.

In some other aspects, however, there are some striking differences between the original and reproduced channel use figures as well.

In some of the figures in the original literature (e.g. figure 2 in the demystifying paper) the channel uses graph clearly slopes down as the error rate increases. In my reproduced figures, this downward slope is missing.

In other figures in the original literature (e.g. the black and green graphs in figure 9 in the demystifying paper) we see a "wave" pattern on top of the "saw tooth" pattern. This "wave" pattern is missing in my reproduced graphs.

Channel use graph for Cascade opt. (2) is different.
----------------------------------------------------

The original channel use graph for algorithm "Cascade opt. (2)" is quite different from the reproduced graph: the original values are higher and have much more wildly swinging saw-teeth.
