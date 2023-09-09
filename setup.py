from setuptools import find_packages, setup

setup(
    name='toloka2python',
    install_requires=[
        'requests',
    ],
    packages = ['toloka2python', 'toloka2python/models'],
    version='0.1.0',
    description='Бібліотека на пітоні для взаємодії з українським торрент-трекером Toloka',
    author='CakesTwix',
    license='GPL3',
)
