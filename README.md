# Description

Realisation of branch and bound algorithm for solving Maximum clique problem using greedy coloring heuristic to estimate upper bound and greedy clique heuristic for lower bound on each step.<br>

Details: http://www.m-hikari.com/ams/ams-2014/ams-1-4-2014/mamatAMS1-4-2014-3.pdf

## Instructions
This is `Python 3.5.2` realisation with usage of `NetworkX` library 

To run script you should specify following parameters:
- `--path` - path to DIMACS-format graph
- `--time` - time limit in seconds


## Test results

Graph name|#Nodes|#Edges|Found clique length|Time (ms)
---|---|---|---|---
miles250.col|128|774|8|1.001
anna.col|138|986|11|355.994
homer.col|561|3258|13|1198.999
huck.col|74|602|11|70.997
le450_5a.col|450|5714|5|11773.576
le450_5b.col|450|5734|5|11867.003
le450_5c.col|450|9803|5|19642.002
le450_5d.col|450|9757|5|18900.578
le450_15b.col|450|8169|15|7223.001
le450_15c.col|450|16680|15|46407.516
le450_15d.col|450|16750|15|50872.791
le450_25a.col|450|8260|25|340.000
le450_25c.col|450|17343|25|44315.806
le450_25d.col|450|17425|25|40426.008

All this graphs are placed in `samples` folder. <br>More of them you can find here: http://mat.gsia.cmu.edu/COLOR/instances.html <br>
Huge ones: http://iridia.ulb.ac.be/~fmascia/maximum_clique/DIMACS-benchmark#detC125.9