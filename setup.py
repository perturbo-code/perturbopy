from setuptools import setup, find_packages
   
setup(
   name='perturbopy',
   version='0.1.0',
   python_requires='>=3.7.12',
   install_requires=[
      'numpy>=1.21.4',
      'pytest',
      'h5py'
   ],
   extras_require={
      'interactive': ['matplotlib>=2.2.0', 'jupyter'],
   },
   packages=find_packages(
      where='./src'
   ),
   package_dir={"": "src"} 
)
