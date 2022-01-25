import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="Safe Url Checker",
    version="0.0.1",
    description="Web service for checking URLs for known malware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lucas Hossack",
    package_dir={"": "urlchecker"},
    packages=setuptools.find_packages(where="urlchecker"),
    install_requires=["Flask>=2.0.2", "pymongo==4.0.1", "sphinx==4.4.0", "furo==2022.1.2"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
