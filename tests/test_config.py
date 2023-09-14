import tempfile
from pathlib import Path
from importlib.resources import files

from ezmsg.gadget.config import load_config

def test_config() -> None:
    config_text = files('ezmsg.gadget').joinpath('ezmsg-gadget.conf').read_text()
    extra_function = 'function.Digitizer.digitizer0'
    with tempfile.TemporaryDirectory() as tmpdir:
        with tempfile.NamedTemporaryFile('w+', dir = tmpdir, suffix = '.conf') as temp_config:
            temp_config.write(config_text)
            temp_config.flush()
            conf_dir = Path(temp_config.name).with_suffix('.d')
            conf_dir.mkdir()
            with tempfile.NamedTemporaryFile('w+', dir = conf_dir) as errata_f:
                errata_f.write(f'[{extra_function}]')
                errata_f.flush()
                config = load_config(Path(temp_config.name))
        
    assert 'device' in config.sections()
    assert 'endpoint' in config.sections()
    assert extra_function in config.sections()
    assert 'dev_addr' in config['function.Ethernet.usb0']

if __name__ == '__main__':
    test_config()