from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='perturbopy',
    version='0.7.0',
    description="Suite of Python scripts for Perturbo testing and postprocessing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7.12',
    include_package_data=True,
    install_requires=[
        'numpy>=1.21.4',
        'pytest',
        'pytest-order',
        'h5py',
        'PyYAML',
        'pytest-profiling',
        'matplotlib>=2.2.0',
        'scipy'
    ],
    extras_require={
        'interactive': ['jupyter', 'pytest-plt'],
    },
    packages=find_packages(where='./src'),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'input_generation=perturbopy.generate_input:input_generation',
            'auto_pipeline = perturbopy.auto_pipeline.auto_pipeline:run_epr_calculation',
        ],
    },
)
