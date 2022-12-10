from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

with open("requirements.txt") as ifd:
    common_requirements = [x.strip() for x in ifd]
    
setup(
    name='pyochre',
    version='0.0.0',
    description='Library for the Open Computational Humanities Research Ecosystem (OCHRE).',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tom Lippincott',
    author_email='tom.lippincott@jhu.edu',
    url='https://github.com/comp-int-hum/ochre-python',
    packages=["pyochre"],
    install_requires=common_requirements
)
