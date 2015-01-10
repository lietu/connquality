from cx_Freeze import setup, Executable
from pip.req import parse_requirements


config = {
    'description': 'ConnQuality',
    'author': 'Janne Enberg',
    'url': 'https://github.com/lietu/connquality',
    'download_url': 'https://github.com/lietu/connquality',
    'author_email': 'janne.enberg@lietu.net',
    'version': '0.1',
    'install_requires': [
        #str(r.req) for r in parse_requirements("requirements.txt")
    ],
    'packages': [
        'connquality'
    ],
    'scripts': [],
    'name': 'connquality'
}

packages = [
    'matplotlib.backends.backend_tkagg',
]

setup(name=config["description"],
      version=config["version"],
      description=config["description"],
      options={
          "build_exe": {
              "packages": packages
          }
      },
      executables=[
          Executable("monitor.py", base=None),
          Executable("graph.py", base=None)
      ]
)