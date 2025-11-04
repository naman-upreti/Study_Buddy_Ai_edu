# why do we use this file 
# to install our package in our local machine we use this file
# what is pip install -e .
# this command install our package in our local machine in editable mode
# so that we can make changes in our package and it will reflect in our local machine
# what is find_packages() function
# this function find all the packages in our project and install them in our local machine
# what is install_requires parameter
# this parameter is used to install all the dependencies of our package in our local machine
# what is requirements.txt file
# this file contains all the dependencies of our package
# what is setup.py file
# this file contains all the information about our package like name, version, author, etc.
# what is -e . in pip install -e .
# this command install our package in our local machine in editable mode



from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="LLMOPS--Study_Buddy_Ai",
    version="0.1",
    author="Naman Upreti",
    packages=find_packages(),
    install_requires = requirements,
)