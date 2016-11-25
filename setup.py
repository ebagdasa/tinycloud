from distutils.core import setup

setup(
    name='TinyCloud',
    version='0.1dev',
    packages=['tinycloud',],
    license='MIT License',
    long_description=open('README.md').read(),
    scripts=['bin/tiny-manager', 'bin/tiny-apps'],
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7'
],
)
