from setuptools import find_packages, setup

setup(
    name="toloka2python",
    install_requires=["requests", "beautifulsoup4"],
    packages=["toloka2python", "toloka2python/models"],
    version="0.2.2",
    description="Бібліотека на пітоні для взаємодії з українським торрент-трекером Toloka",
    author="CakesTwix",
    license="GPL3",
)
