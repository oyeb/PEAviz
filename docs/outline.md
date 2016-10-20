# Relevant

* [GEATbx](http://www.geatbx.com/docu/algindex-01.html#TopOfPage)
    - Technical, formal definitions of GA elements
    - Refer if you have doubts like _"what exactly happens in a tournament selection, and how many are selected?"_

## Selection and Population size invariance

`selection` chooses which individuals _survive the generation_ are to be used as parents _(ie. are able to mate, since they survived)_.
The others die and are lost.
This brings up the obvious question, how does population-size remain constant?

**`selection` does not ensure that all _chosen_ individuals are unique!**
This fact is not hard to digest when the initial population is randomly generated -- which has a (very unlikely) chance of creating non-distinc individuals.
Imagine the selection is over. Now we crossover and/or mutate these guys. `crossover` maintains the size of population, ie `k` parents -> `k` children (most crossover strategies).
`mutate` also preserves size of population.
>Infact most implementations modify the parents "in-place".

This is a bit crazy because this allows 1 individual to be _selected_ many times, and hence spawn multiple offsprings, in just a single generation!
Does that affect us in any detrimental way? Not at all, it's just shocking that's all.

#Irrelevant

## Inspiration, Goal

Look at the Gold and silver winners in 2016 of the ["Humie Contest"](http://www.human-competitive.org/)

## Genetic Programming

http://www.genetic-programming.com/ is curated and (not actively) maintained by John Koza, founding father of the field.
The [PyEvolve](www.intellovations.com/pyevolve/) page lists many other GA resources and contests some of which are active.

## Python

[PyEvolve](www.intellovations.com/pyevolve/) is a mature platform.
This PyCon 2011 presentation by Eric Floehr is *the [best intro]*(PyCon2011_GAGP_talk.pdf) to PyEvolve.
A [technical paper](pyevolve_paper.pdf) on PyEvolve by the author, ...
Get PyEvolove from [here]()