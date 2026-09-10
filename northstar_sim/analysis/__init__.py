"""Standalone analysis fixtures using the simulator's broker transitions.

These files are deliberately outside ``northstar_sim/*.py`` so that adding an
analysis does not invalidate a previously frozen study manifest. See
``northstar_sim.study.source_hashes``: it hashes the modules that determine
episode outcomes, and nothing here is reachable from ``run_episode``.
``verify_project.sources`` separately hashes these analysis implementations.
"""
