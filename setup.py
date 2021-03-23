from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name="whoop-sandbox",
    version="0.0.1",
    author="Carter Allen",
    author_email="jeffmshale@gmail.com",
    description="a whooptastic playground",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/b-carter-allen/whoop-sandbox/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.6.9",
        "License :: OSI Approved :: CC0 1.0 Universal",
    ],
)
