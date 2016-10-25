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

1. [Install Gephi](https://gephi.org/users/install/) for your system.
Download the GraphStream plugin from the [Gephi Plugin Marketplace](https://marketplace.gephi.org/). Installation instructions are [here](https://marketplace.gephi.org/faq/).
2. [Install `deap`](http://deap.readthedocs.io/en/master/installation.html). I recommend that you clone the source repository in addition to installation.
3. Clone [my fork](https://github.com/arrow-/GephiStreamer) of [GephiStreamer](https://github.com/totetmatt/GephiStreamer/) into `PEAviz/`
4. Install GephiStreamer by:
```sh
$ pwd
> .../PEAviz/GephiStreamer
$ sudo python setup.py install
```

# Usage
`$ python basic-test.py`
Or with a few trivial changes, you could run an ipython session. You'll be able to inspect `POP`.
```
$   ipython
>>> from basic-test import *
>>> POP
...
```

**`onemax.py` is an illustrative example of the module.**

>**Note**
Only scripts placed in `PEAviz/` will be _(automatically)_ able to detect and use the `peaviz` module.

# Results
**Testing `onemax.py`**

Force Atlas Layout: [Animated `gif` (2.5MB)][onemax-gif-raw]

A different layout of the same graph:
![img-onemax-gephi-sfdp][graphviz-gif]

_This work is part of our Undergaduate Degree Course Work._

[onemax-gif]: docs/images/onemax.gif "Animated gif of OneMax GA"
[onemax-gif-raw]: https://raw.githubusercontent.com/arrow-/PEAviz/master/docs/images/onemax.gif
[graphviz-gif]: docs/images/graphviz-sfdp.png "Animated gif of OneMax GA"