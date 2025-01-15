from setuptools import setup, find_packages

setup(
    name="crx-toolkit",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "requests>=2.26.0",
        "cryptography>=3.4.0",
    ],
    entry_points={
        'console_scripts': [
            'crx-toolkit=crx_toolkit.cli:cli',
        ],
    },
    author="JT",
    author_email="bineanzhou@gmail.com",
    description="A cross-platform Python library for CRX file operations",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bineanzhou/crx-toolkit",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
) 