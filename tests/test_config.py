import tempfile
from pathlib import Path
from importlib.resources import files

from ezmsg.gadget.config import GadgetConfig

def test_config() -> None:
    config_text = files('ezmsg.gadget').joinpath('ezmsg-gadget.conf').read_text()
    extra_function = 'function.Mouse.mouse1'
    with tempfile.TemporaryDirectory() as tmpdir:
        with tempfile.NamedTemporaryFile('w+', dir = tmpdir, suffix = '.conf') as temp_config:
            temp_config.write(config_text)
            temp_config.flush()
            conf_dir = Path(temp_config.name).with_suffix('.d')
            conf_dir.mkdir()
            with tempfile.NamedTemporaryFile('w+', dir = conf_dir) as errata_f:
                errata_f.write(f'[{extra_function}]')
                errata_f.flush()
                config = GadgetConfig(Path(temp_config.name))
        
    assert config.gadget_name == 'g1'
    assert config.endpoint_remote_addr == ('localhost', 25978)
    assert extra_function.split('.')[-1] in config.functions
    assert 'dev_addr' in config.functions['usb0'][1]

if __name__ == '__main__':
    test_config()