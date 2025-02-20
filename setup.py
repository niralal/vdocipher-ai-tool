from setuptools import setup, find_packages

setup(
    name="subtitle-generator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "openai",
        "requests",
        "python-dotenv",
        "ffmpeg-python",
    ],
) 