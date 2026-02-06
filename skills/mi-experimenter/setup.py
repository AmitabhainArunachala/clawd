from setuptools import setup, find_packages

setup(
    name="mi-experimenter",
    version="0.1.0",
    description="Mechanistic Interpretability Experimental Framework with R_V measurement",
    author="AIKAGRYA Research Team",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "transformers>=4.35.0",
        "accelerate>=0.24.0",
    ],
    extras_require={
        "rv": ["rv-toolkit @ file://localhost/Users/dhyana/mech-interp-latent-lab-phase1/rv_toolkit"],
        "dev": ["pytest>=7.0.0", "black", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "mi-experimenter=mi_experimenter.cli:main",
        ],
    },
)
