# PEAviz
_Python Evolutionary Algorithm Visualistaion toolkit on DEAP_

PEAviz bridges [DEAP](https://www.github.com/deap/deap), [Gephi](https://github.com/gephi/gephi) and a fairly new way of visualizing the dynamics of evolution process, using Complex Networks.

PEAViz monitors the evolution and pipes events (and the graph) to Gephi in real time using Gephi's [GraphStream API](https://github.com/gephi/gephi/wiki/GraphStreaming).

To find out more about the approach refer [(pdf)](http://www.complex-systems.com/pdf/20-2-5.pdf):
>Zelinka I, Davendra D, Senkerik R and Jasek R (2011) Do Evolutionary Algorithms Dynamics Create Complex Network Structures? Complex Systems. Vol. 20, No. 4, Pp. 127-140, ISSN 0891-2513.

You can find good resources on GA implementation, theory, etc in `docs/outline.md`.

# Why DEAP
DEAP is a very flexible framework to run evoultionary algorithms. We can fine tune all aspects of the `evolution` and `individuals`.

# Why Gephi
The result of PEAViz analysis is a graph, which _could_ be a CN. Gephi is one of the best graph analysis tools.
With the GraphStream API we can not only monitor the evolution dynamics in real-time, but can also send feedback into the (DEAP) evolution process. Imagine the power of GAs when they are _self_-governed over a feedback loop!

# Setup
[Install Gephi](https://gephi.org/users/install/) for your system.
Download the GraphStream plugin from the [Gephi Plugin Marketplace](https://marketplace.gephi.org/). Installation instructions are [here](https://marketplace.gephi.org/faq/).
[Install `deap`](http://deap.readthedocs.io/en/master/installation.html).

# Usage
`$ python onemax.py`
Or with a few trivial changes, you could run an ipython session. You'll be able to inspect `POP`.
```
$ipython
>>> from onemax import *
>>> POP
...
...
```

# Results

This work is part of our Undergaduate Degree Course Work.