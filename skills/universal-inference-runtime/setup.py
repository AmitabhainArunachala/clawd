from setuptools import setup, find_packages

with open("SKILL.md", "r") as f:
    long_description = f.read()

setup(
    name="universal-inference-runtime",
    version="0.1.0",
    description="Multi-backend inference runtime for AI models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AIKAGRYA Research",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "llama": ["llama-cpp-python>=0.2.0"],
        "all": ["llama-cpp-python>=0.2.0", "numpy>=1.24.0"],
    },
    entry_points={
        "console_scripts": [
            "universal-inference=universal_inference.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
