from distutils.core import setup

setup(
    name='TinyCloud',
    version='0.4dev',
    packages=['tinycloud',],
    license='BSD',
    long_description=open('README.md').read(),
    scripts=['bin/tiny-add-node', 'bin/tiny-add-app', 'bin/tiny-delete-app', 'bin/tiny-draw', 'bin/tiny-get-apps',
             'bin/tiny-get-servers', 'bin/tiny-delete-node', 'bin/tiny-add-flow', 'bin/tiny-deploy'],
    install_requires=[
        'ansible',
        'redis',
        'networkx',
        'scipy',
        'fabric', 'knapsack'
      ],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.7',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
],
)
