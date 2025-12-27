from setuptools import setup, find_packages

setup(
    name="mowen-converter",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'convert-to-mowen=mowen_converter.converter:main',
        ],
    },
    install_requires=[],
    author="Gevin",
    description="A tool to convert Markdown to Mo Wen style",
)
