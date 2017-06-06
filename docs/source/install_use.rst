.. include:: role_defs.rst

Installation and Usage
======================

Installation
------------

*PEAviz has not yet been pacakged, see* `#5 <https://github.com/arrow-/PEAviz/issues/5>`_

#. Get the `latest release <https://github.com/arrow-/PEAviz/releases>`_ (|release|), from the GitHub repo.
#. Install the python requirements:

    - ``pip install -r requirements.txt``
#. *(Optional)* Install ``graph-tool``. Refer `official instructions <https://git.skewed.de/count0/graph-tool/wikis/installation-instructions>`_.

Usage
-----

.. seealso:: :ref:`arch:Architecture`

* Implement your GA in DEAP_.
* Use ``peaviz`` elements to track the dynamics.
    - Decide **Encoding Strategy**, *or use the default.*
    - Implement a **Tracker Interface** for your Encoding Strategy.
    - Use an Adapter, *or implement your own.*
* Execute GA, upon completion PEAviz provides a network.
* Export the network to desired analysis tool *(we use ``graph-tool``)*.
* Analyse.

