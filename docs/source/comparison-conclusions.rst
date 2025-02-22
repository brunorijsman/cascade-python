*******************************************************
Conclusions from Comparison of Results with Literature.
*******************************************************

Here we summarize some of the differences that we observed in the reproduced figures as compared to the literature.

Less detail.
------------

The graphs in the "demystifying the Information Reconciliation Protocol Cascade” paper are much more detailed because they executed 10,000 (or sometimes even 100,000 or 1,000,000) runs per data point, whereas we only ran 1,000 runs per data point. Our Python implementation was is not fast enough to execute more than 1,000 runs per data point. It already took us about 5 days to run all the experiments on 2xlarge m5 instance on AWS with just 1,000 runs per data point. We are in the process of re-implementing Cascade in C++ which will hopefully allow for more runs per data point.

Standard deviation.
-------------------

The graphs in the original papers do not have any indication of the standard deviation (i.e. no error bars). We have that information for all experiments, although we don't show it in all graphs - we omit it if it would make the graph too noisy.

Differences in the detailed shape of the channel use graph.
-----------------------------------------------------------

In many respects, most of my reproduced channel use figures match the figures in the original literature quite well. The overall shape matches quite well. The appearance of saw-tooth patterns matches quite well. The numerical value matches quite well.

In some other aspects, however, there are some striking differences between the original and reproduced channel use figures as well.

In some of the figures in the original literature (e.g. figure 2 in the demystifying paper) the channel uses graph clearly slopes down as the error rate increases. In my reproduced figures, this downward slope is missing.

In other figures in the original literature (e.g. the black and green graphs in figure 9 in the demystifying paper) we see a "wave" pattern on top of the "saw tooth" pattern. This "wave" pattern is missing in my reproduced graphs.

Channel use graph for Cascade opt. (2) is different.
----------------------------------------------------

The original channel use graph for algorithm "Cascade opt. (2)" is quite different from the reproduced graph: the original values are higher and have much more wildly swinging saw-teeth.
