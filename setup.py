from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

version = '1.2.1'

setup(
    name = 'sysexecute',
    packages = ['sysexecute'], # this must be the same as the name above
    version = version,
    description = 'A library for simplified executing of system commands',
    long_description = long_description,
    long_description_content_type='text/markdown',  # This is important!
    author = 'Jason Harris',
    author_email = 'jason@jasonfharris.com',
    license='MIT',
    url = 'https://github.com/jasonfharris/sysexecute',
    download_url = 'https://github.com/jasonfharris/sysexecute/tarball/'+version,
    keywords = ['execute', 'shell', 'system'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Shells',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
        ],
    install_requires = ['argcomplete']
)