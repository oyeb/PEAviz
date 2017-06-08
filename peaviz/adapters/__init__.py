#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib

from .adapter_base import AdapterBase

if importlib.util.find_spec('graph_tool') is not None:
    from .graph_adapter import GraphAdapter
