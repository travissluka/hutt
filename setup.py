import setuptools

setuptools.setup(
  name='hutt',
  version='0.0.1',
  author='Travis Sluka',
  author_email='tsluka@ucar.edu',
  description='Helpful Utility for Testing Tutorials',
  url='https://github.com/travissluka/hutt',
  package_dir={'': 'src'},
  packages=setuptools.find_packages(where='src'),
  classifiers=[
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
  ],
  setup_requires=["setuptools-git-versioning"],
  setuptools_git_versioning={
    "enabled": True,
  },
  python_requires='>=3.6',
  install_requires=[
    'click',
    'ruamel.yaml',
    'gdown',
  ],
  entry_points={
    'console_scripts': [
      'hutt = hutt.bin.hutt:cli',
    ],
  },
)
