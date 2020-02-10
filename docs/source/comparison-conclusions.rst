*******************************************************
Conclusions from Comparison of Results with Literature.
*******************************************************

Here we summarize some of the differences that we observed in the reproduced figures as compared to the literature.

Unrealistic efficiency.
-----------------------

My cascade-python code produced "efficiency vs bit error rate" graphs that matched the results in the literature very well.

However, I could only obtain a good match between my results and the literature results if I used an extremely unrealistic definition of efficiency (this is called "unrealistic_efficiency" in the code).

The "spirit" of the definition of "reconciliation efficiency" it to compare the actual number of bits exchanges between Alice and Bob during the reconciliation protocol and compare it with the theoretical minimum number of bits.

For example, if the theoretical minimum is 200 bits and we actually exchanged 220 bits, then the reconciliation efficiency is 220/200 = 1.10, meaning that we used 10% more bits than the theoretical minimum.

Every time Bob asks Alice to compute and reveal the correct parity for some block, some bits are exchanged. To compute the reconciliation efficiency we need to add up all these exchanged bits and compare the total number of exchanged bits with the theoretical minimum. This is what I call the "realistic_efficiency" in my code. However, if I do this, I end up with efficiencies that are way worse by several orders of magnitude than the ones reported in the literature.

To accurately reproduce the results reported in the literature I had to make a very unrealistic assumption: every time Bob asks Alice to compute and reveal the correct parity of a block, I count that as a single bit of information exchanged. When I do that, my results and the results from the literature match almost perfectly.

Clearly, this is not realistic. Bob asking Alice for the correct parity actually uses much more than one bit: Bob has to identify the block and the shuffling order which takes way more than one bit. Hence, I call this "unrealistic_efficiency" in my code.

Less detail.
------------

The graphs in the "demystifying the Information Reconciliation Protocol Cascade” paper are much more detailed because they executed 10,000 (or sometimes even 100,000 or 1,000,000) runs per data point, whereas we only ran 1,000 runs per data point. Our Python implementation was is not fast enough to execute more than 1,000 runs per data point. It already took us about 5 days to run all the experiments on 2xlarge m5 instance on AWS with just 1,000 runs per data point. We are in the process of re-implementing Cascade in C++ which will hopefully allow for more runs per data point.

Standard deviation.
-------------------

The graphs in the original papers do not have any indication of the standard deviation (i.e. no error bars). We have that information for all experiments, although we don't show it in all graphs - we omit it if it would make the graph too noisy.

Missing slow decrease in channel uses.
--------------------------------------

The figures reported in the literature show that the number of channel uses first sharply increases as the bit error rate increases from 0.00 to 0.30. After that the number of channel uses slowly decreases again. We don't see this latter slow decrease in our results. I currently have no explanation for this difference.
