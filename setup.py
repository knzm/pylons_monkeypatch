from codecs import open as codecs_open
from setuptools import setup, find_packages

# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pylons-monkeypatch',
    version='0.0.1',
    description=u"Collection of monkey patches for Pylons projects",
    long_description=long_description,
    keywords='',
    license='MIT',
    author=u"Nozomu Kaneko",
    author_email='nozom.kaneko@gmail.com',
    url='https://github.com/knzm/pylons_monkeypatch',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    extras_require={
        'test': ['pytest'],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Framework :: Pylons",
        "Programming Language :: Python",
    ],
)
