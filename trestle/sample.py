# DO NOT COMMIT TO DEVELOP

import pathlib
import random

def add_a_banana(path: pathlib.Path) -> pathlib.Path:
    """Here we do some mindless compute then add a number of bananas."""
    for ii in range(random.randint(1,101)):
        return path / f'with_{ii}_bananas'
