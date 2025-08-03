from setuptools import setup, find_packages

setup(
    name="2do",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "openai>=1.0.0",
        "anthropic>=0.20.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "rich>=13.0.0",
        "PyGithub>=2.0.0",
        "GitPython>=3.1.0",
        "playwright>=1.40.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "2do=twodo.cli:main",
        ],
    },
    author="STAFE GROUP AB",
    description="2DO - Intelligent AI model routing and multitasking CLI tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/STAFE-GROUP-AB/AI-Redirector",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)