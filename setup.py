import setuptools

setuptools.setup(
    name='ezmsg-gadget',
    packages=setuptools.find_namespace_packages(include=['ezmsg.*']),
    zip_safe=False
)
