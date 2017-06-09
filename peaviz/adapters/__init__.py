"""
The :mod:`~peaviz.adapters` module contains all the adapters which are
compatible with all the trackers in :mod:`~peaviz.trackers`.
"""

import importlib

if importlib.util.find_spec('graph_tool') is not None:
    try:
        from .graph_adapter import GraphAdapter
    except ImportError:
        pass
