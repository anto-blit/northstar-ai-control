"""Portable offline replay of frozen G1-D code, with stable USD aggregation.

Python 3.12 changed sum's floating-point algorithm. The original experiment ran
on 3.14; 3.10 adds E's costs to 0.08133099999999999 instead of 0.081331. Use
math.fsum only for float sums during replay. Integer outcome counts, parsing,
frozen source bytes, saved responses, and saved scores are not changed.
"""
import builtins
import importlib.util
import math
from pathlib import Path


def stable_sum(values, start=0):
    values = list(values)
    if isinstance(start, float) or any(isinstance(value, float) for value in values):
        return math.fsum([start, *values])
    return builtins.sum(values, start)


def main():
    source = Path(__file__).with_name("development.py")
    spec = importlib.util.spec_from_file_location("frozen_development", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.sum = stable_sum
    module.score()


if __name__ == "__main__":
    main()
