# Replication Contexts Analyzer

Replication Contexts Analyzer (from now on "RCA"), is a Web Based Tool that uses the information coming from the autosupport files to identify bottlenecks and to fingerpoint the reasons why one or multiple replication contexts might be lagging or are under performing. 

RCA uses the metrics found in the "Lrepl Client Time Stats" and plots a graph for every replication context selected, displaying also a table with the times in percentage spent by every replication operation within that replication context.

The tool also provides actionable steps to mitigate or resolve replication lags, or to improve the performance of any replication context under analysis.

A PDF report can be obtained with all the information presented on the screen, and it can be used to argue with the customer (with proper data), why a replication is lagging and what can be done to improve the replication lag or replication "under performing" situation.

RCA is based on a modern Web Based GUI that simplifies the usage and is suitable for a wider audience.

How to access RCA?

RCA can be accessed from any web browser (although Google Chrome is recommended), just by simply navigating to the following URL:

http://ddsup01/RCA/

How to use RCA?

RCA can support the following modes of operation: 

1) Direct Upload from our computer of one or multiple autosupport files representing a source Data Domain.
2) Path specification mode: where we provide the path to a valid location inside the evidence server that should contain valid autosupport files coming from the source Data Domain.

In both cases, the tool will allow us to select one or two autosupport files.

If just one autosupport file is selected, then the information displayed will come from the "Lrepl Client Time Stats" of the specified autosupport file.

If two autosupport files are selected, then the tool will check the consistency between autosupports (basically if the are coming from the same Data Domain system, if they have the same number of Lrepl Client Time Stats metrics, and if the same number of contexts are found) Any context that is just present in one of the two autosupport files, will be discarted.

Once the consistency of the autosupport files have been validated, the delta difference of the "LRepl Client Time Stats" will be calculated for every valid replication context found.

Why delta difference matters? As "Lrepl Client Time Stats" are cumulative metrics, the metrics do accumulate forever (or until you restart the filesystem).
Hence the information coming from just one autosupport file represents what a context has being doing since the beggining of the time, or since the latest File System restart. 

On the opposite "Delta Lrepl Client Time Stats" is the difference in the "Lrepl Client Time Stats" metrics between two autosupports, and can be used to know the time spent by every context in each of the replication operations between the dates of the two selected autosupports.

Or in other words:

If we select just one autosupport file, then the information presented on the reports will be historical information since the beginning of the time or since the latest FS restart.
If we select two autosupport files, then the information presented on the reports will be based on the delta difference between the two "GENERATED_ON" dates of the autosupports.

Delta Difference (selecting two autosupport files) can be used to see what is happening for a replication context between two dates, rather than since the beginning of the time.

Usage examples
