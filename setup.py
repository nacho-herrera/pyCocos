import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyCocos",
    version="0.2.0",
    author="Nacho Herrera",
    author_email="github@nachoherrera.com.ar",
    description="Python connector for Cocos Capital's Rest APIs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nacho-herrera/pyCocos",
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests>=2.28.2',
        'simplejson>=3.19.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development"
    ],
)
