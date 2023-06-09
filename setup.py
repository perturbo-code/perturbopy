from setuptools import setup, find_packages
   
setup(
   name='perturbopy',
   version='0.1.0',
   python_requires='>=3.7.12',
   install_requires=[
      'numpy>=1.21.4',
      'pytest',
      'h5py',
      'hdfdict',
      'PyYAML',
      'pytest-profiling',
      'matplotlib>=2.2.0',
      'scipy'
   ],
   extras_require={
      'interactive': ['jupyter', 'pytest-plots'],
   },
   packages=find_packages(
      where='./src'
   ),
   package_dir={"": "src"} 
)
