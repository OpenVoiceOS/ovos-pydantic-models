from setuptools import setup, find_packages
from os import path, getenv

BASEDIR = path.abspath(path.dirname(__file__))


def get_version():
    version_vars = {}
    with open(path.join(BASEDIR, 'ovos_pydantic_models', 'version.py')) as f:
        exec(f.read(), version_vars)
    major = version_vars['VERSION_MAJOR']
    minor = version_vars['VERSION_MINOR']
    build = version_vars['VERSION_BUILD']
    alpha = version_vars.get('VERSION_ALPHA', 0)
    version = f"{major}.{minor}.{build}"
    if alpha:
        version += f"a{alpha}"
    return version


def get_requirements(requirements_filename: str):
    requirements_file = path.join(BASEDIR, 'requirements', requirements_filename)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip() and not r.strip().startswith('#')]

    for i, req in enumerate(requirements):
        r, operator, v = req, None, None
        if '>=' in req:
            r, v = req.split('>=')
            operator = '>='
        elif '<=' in req:
            r, v = req.split('<=')
            operator = '<='
        if operator and getenv('MYCROFT_LOOSE_REQUIREMENTS'):
            requirements[i] = f'{r}>={v.split(",")[0].strip()}'
    return requirements


with open(path.join(BASEDIR, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ovos-pydantic-models',
    version=get_version(),
    author='OpenVoiceOS',
    author_email='support@openvoiceos.org',
    description='Pydantic models for OpenVoiceOS MessageBus messages — the typed protocol reference.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/OpenVoiceOS/ovos-pydantic-models',
    license='Apache-2.0',
    packages=find_packages(exclude=['test', 'test.*']),
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Home Automation',
    ],
    python_requires='>=3.10',
    install_requires=get_requirements('requirements.txt'),
    extras_require={
        'dev': get_requirements('extra-dev.txt'),
    },
)
