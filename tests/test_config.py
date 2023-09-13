import os
from pathlib import Path

from ezmsg.gadget.config import load_config

def test_config() -> None:
    script_path = os.path.realpath(os.path.dirname(__file__))
    config = load_config(Path(script_path) / 'configs' / 'ezmsg-gadget.conf')
    print(config.sections())

if __name__ == '__main__':
    test_config()