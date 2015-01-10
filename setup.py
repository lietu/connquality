try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pip.req import parse_requirements


config = {
    'description': 'ConnQuality',
    'author': 'Janne Enberg',
    'url': 'https://github.com/lietu/connquality',
    'download_url': 'https://github.com/lietu/connquality',
    'author_email': 'janne.enberg@lietu.net',
    'version': '0.1',
    'install_requires': [
        str(r.req) for r in parse_requirements("requirements.txt")
    ],
    'packages': [
        'connquality'
    ],
    'scripts': [],
    'name': 'connquality'
}

setup(**config)
