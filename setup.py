import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="gopro-overlay",
    version="0.0.0.1",
    description="Overlay graphics dashboards onto GoPro footage",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/time4tea/gopro-dashboard-overlay",
    author="James Richardson",
    author_email="james+gopro@time4tea.net",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["gopro_overlay"],
    include_package_data=True,
    install_requires=[],
    scripts=[
        "bin/gopro-dashboard.py",
        "bin/gopro-to-gpx.py"
    ],
    entry_points={
        "console_scripts": []
    },
)
