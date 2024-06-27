from setuptools import setup, find_packages

setup(
    name='test-rag',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'mistralai',
        'pandas',
        'numpy',
        'scikit-learn',
    ],
)
