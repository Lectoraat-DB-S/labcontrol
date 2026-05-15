.. _intro-design:

Design of labcontrol
====================

This section contains a number of sections about the question "Why Labcontrol is like it is". For the impatient:

1. Sometimes certain features of Labcontrol exists because it was the prior intention to have it that way. For example, the factory pattern
    responsible for the creation of all instrument controlling objects was an goal set long ago, as part of the Python programming 
    learning curve.
2. More likely, changes made exists because Labcontrol didn't work properly (any more) or some parts of became a burden in programming 
    efficiently. 

Design Documents
================
.. toctree::
    :maxdepth: 2

    parallelism.rst
    
    