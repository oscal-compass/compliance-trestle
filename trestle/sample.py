# DO NOT COMMIT TO DEVELOP
"""Testing for sonar."""
import pathlib
import random


def add_a_banana(path: pathlib.Path) -> pathlib.Path:
    """Add a path which is based on random bananas."""
    cryptogen = random.SystemRandom()
    for ii in range(cryptogen.randrange(100)):
        a = ii
    return path / f'with_{a}_bananas'
