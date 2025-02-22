from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="remote-expose",
    version="0.0.1",
    author="Pablo Schaffner",
    author_email="pablo@puntorigen.com",
    description="A Python package to expose local files through a public URL using ngrok",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/puntorigen/remote-expose",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyngrok>=5.0.0",
    ],
)
