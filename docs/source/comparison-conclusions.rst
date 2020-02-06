*******************************************************
Conclusions from Comparison of Results with Literature.
*******************************************************

Less detail.
------------

The graphs in the "demystifying the Information Reconciliation Protocol Cascade” paper are much more detailed because they executed 10,000 (or sometimes even 100,000 or 1,000,000) runs per data point, whereas we only ran 1,000 runs per data point. Our Python implementation was is not fast enough to execute more than 1,000 runs per data point. It already took us about 5 days to run all the experiments on 2xlarge m5 instance on AWS with just 1,000 runs per data point. We are in the process of re-implementing Cascade in C++ which will hopefully allow for more runs per data point.

Standard deviation.
-------------------

The graphs in the original papers do not have any indication of the standard deviation (i.e. no error bars). We have that information for all experiments, although we don't show it in all graphs - we omit it if it would make the graph too noisy.
