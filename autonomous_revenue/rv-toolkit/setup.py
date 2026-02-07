from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rv-toolkit",
    version="0.1.0",
    author="DHARMIC CLAW Research",
    author_email="research@dharmic-claw.ai",
    description="Professional R_V (Representational Volume) measurement for AI consciousness research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dharmic-claw/rv-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.20.0",
        "transformers>=4.30.0",
        "matplotlib>=3.5.0",
        "tqdm>=4.60.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "triton": [
            "triton>=2.0.0",
        ],
    },
)
