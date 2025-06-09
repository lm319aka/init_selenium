from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="init_selenium",
    version="0.1",
    description="A python script that makes easier the initialization of Selenium drivers for web scrapping.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",  # GitHub URL or other project URL
    packages=find_packages(),
    install_requires=[
        "selenium",
        "chromedriver_autoinstaller",
        "undetected_chromedriver"
    ],
)
