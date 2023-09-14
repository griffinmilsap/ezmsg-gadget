
import typing
import subprocess

from pathlib import Path
from importlib.resources import files

def _confirm_prompt(question: str, yes: bool = False) -> bool:
    reply = None if not yes else ""
    while reply not in ("", "y", "n"):
        reply = input(f"{question} (Y/n): ").lower()
    response = (reply in ("", "y"))
    if response:
        print(f'ACTION: {question}')
    return response

_CONFIG_DIR = lambda root: root / 'etc'
_MODULES_DIR = lambda root: _CONFIG_DIR(root) / 'modules-load.d'
_SERVICE_DIR = lambda root: root / Path('lib/systemd/system')

CONFIG_FILE = 'ezmsg-gadget.conf'
BOOT_SERVICE_FILE = 'ezmsg-gadget.service'
ENDPOINT_SERVICE_FILE = 'ezmsg-gadget-endpoint.service'

def install(
        root: Path = Path('/'), 
        boot_service: bool = True, 
        endpoint_service: bool = False, 
        yes: bool = False
    ) -> None:

    # CONFIGURE KERNEL MODULES
    modules_dir = _MODULES_DIR(root)

    if _confirm_prompt(f'Add dwc2 to {modules_dir}', yes):
        with open(modules_dir / 'dwc2', 'w') as f:
            f.write('dwc2')

    if _confirm_prompt(f'Add libcomposite to {modules_dir}', yes):
        with open(modules_dir / 'libcomposite', 'w') as f:
            f.write('libcomposite')

    data_files = files('ezmsg.gadget')

    # ADD CONFIG FILE
    config_dir = _CONFIG_DIR(root)
    config_file = 'ezmsg-gadget.conf'
    if _confirm_prompt(f'Add {config_file} to {config_dir}'):
        with open(config_dir / config_file, 'w') as config_f:
            config_f.write(data_files.joinpath(config_file).read_text())
    
    # ADD BOOT SERVICE
    service_dir = _SERVICE_DIR(root)
    boot_service_enabled = False

    if boot_service:
        print('Boot service: enumerate devices on boot')
        print('Why? Activating ezmsg-gadget requires root, so do it on boot automatically')
        if _confirm_prompt(f'Write {BOOT_SERVICE_FILE} to {service_dir}', yes):
            with open(service_dir / BOOT_SERVICE_FILE, 'w') as f:
                f.write(data_files.joinpath(BOOT_SERVICE_FILE).read_text())
            if _confirm_prompt('Issue "systemctl daemon reload"', yes):
                subprocess.run('systemctl daemon reload', shell = True)

    # ENABLE BOOT SERVICE
    result = subprocess.run(
        f'systemctl is-enabled {BOOT_SERVICE_FILE}', 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE,
        shell = True
    )

    # CHECK IF BOOT SERVICE ENABLED
    if result.stdout == b'enabled':
        print('Boot service enabled')
        boot_service_enabled = True
    elif result.stdout == b'disabled':
        if boot_service and _confirm_prompt(f'Enable {BOOT_SERVICE_FILE}', yes):
            subprocess.run(f'systemctl enable {BOOT_SERVICE_FILE}', shell = True)
            boot_service_enabled = True
    else:
        print('Boot service not installed or enabled')

    # ADD ENDPOINT SERVICE
    if endpoint_service:
        print('Endpoint service: run an ezmsg endpoint to connect to remote graph server on boot')
        print('Why? This software is likely running on a headless single-board computer')
        if not boot_service_enabled:
            print('WARNING: This service requires the boot service to run.')
        if _confirm_prompt(f'Write {ENDPOINT_SERVICE_FILE} to {service_dir}', yes):
            with open(service_dir / ENDPOINT_SERVICE_FILE, 'w') as f:
                f.write(data_files.joinpath(ENDPOINT_SERVICE_FILE).read_text())
                if _confirm_prompt('Issue "systemctl daemon reload"', yes):
                    subprocess.run('systemctl daemon reload', shell = True)

    # ENABLE ENDPOINT SERVICE
    result = subprocess.run(
        f'systemctl is-enabled {ENDPOINT_SERVICE_FILE}', 
        stdout = subprocess.PIPE, 
        stderr = subprocess.PIPE,
        shell = True
    )

    # CHECK IF ENDPOINT SERVICE ENABLED
    if result.stdout == b'enabled':
        print('Endpoint service enabled')
    elif result.stdout == b'disabled':
        if endpoint_service and _confirm_prompt(f'Enable {ENDPOINT_SERVICE_FILE}', yes):
            subprocess.run(f'systemctl enable {ENDPOINT_SERVICE_FILE}', shell = True)
    else:
        print('Endpoint service not installed or enabled')

    print("Install completed.  Reboot encouraged.")

def uninstall(root: Path = Path('/'), yes: bool = False) -> None:

    # STOP/DISABLE SERVICES
    service_dir = _SERVICE_DIR(root)

    services: typing.List[Path] = [
        service_dir / BOOT_SERVICE_FILE,
        service_dir / ENDPOINT_SERVICE_FILE,
    ]

    daemon_reload = False
    for service in services:
        result = subprocess.run(
            f'systemctl is-enabled {service.name}', 
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE,
            shell = True
        )

        if result.stdout == b'enabled' and _confirm_prompt(f'Disable {service.name}', yes):
            subprocess.run(f'systemctl disable {ENDPOINT_SERVICE_FILE}', shell = True)

        if service.exists() and _confirm_prompt(f'Remove {service}', yes):
            service.unlink()
            daemon_reload = True

    if daemon_reload and _confirm_prompt('Issue "systemctl daemon reload"', yes):
        subprocess.run('systemctl daemon reload', shell = True)

    modules_dir: Path = _MODULES_DIR(root)
    config_dir: Path = _CONFIG_DIR(root)

    # REMOVE ALL OTHER INSTALLED FILES
    files = services + [
        modules_dir / 'dwc2',
        modules_dir / 'libcomposite',
        config_dir / CONFIG_FILE
    ]

    for f in files:
        if f.exists() and _confirm_prompt(f'Remove {f}', yes):
            f.unlink()

    print("Uninstall completed.  Reboot encouraged.")