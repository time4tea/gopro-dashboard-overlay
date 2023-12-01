import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

requires = [
    "pillow==9.4.0",
    "pint==0.22",
    "geotiler==0.14.7",
    "gpxpy==1.6.1",
    "fitdecode==0.10.0",
    "geographiclib==1.52",
    "progressbar2==4.2.0",
    "requests==2.31.0",
    "sqlitedict==2.1.0",
]

test_requirements = [
    "pytest"
]

setup(
    name="gopro-overlay",
    version="0.115.0",
    description="Overlay graphics dashboards onto GoPro footage",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/time4tea/gopro-dashboard-overlay",
    author="James Richardson",
    author_email="james+gopro@time4tea.net",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Environment :: Console",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
    ],
    packages=[
        "gopro_overlay",
        "gopro_overlay.gpmf",
        "gopro_overlay.gpmf.visitors",
        "gopro_overlay.icons",
        "gopro_overlay.layouts",
        "gopro_overlay.widgets",
        "gopro_overlay.widgets.cairo",
    ],
    install_requires=requires,
    tests_require=test_requirements,
    scripts=[
        "bin/gopro-contrib-data-extract.py",
        "bin/gopro-cut.py",
        "bin/gopro-dashboard.py",
        "bin/gopro-extract.py",
        "bin/gopro-join.py",
        "bin/gopro-layout.py",
        "bin/gopro-rename.py",
        "bin/gopro-to-csv.py",
        "bin/gopro-to-gpx.py",
        "bin/gopro-debug.py",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    entry_points={
        "console_scripts": []
    },
    project_urls={
        'Source': 'https://github.com/time4tea/gopro-dashboard-overlay',
    },
)
