"""
This file provides import context for test modules.

Importing modules under test from this file allows tests to be run from different root directories.
i.e. we can run unittest -m discover from the project root directory, or run a test inside tests directly.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from urlchecker import database_abc, urlchecker, dbm_adaptor
