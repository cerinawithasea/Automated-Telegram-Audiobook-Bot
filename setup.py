from setuptools import setup, find_packages

setup(
    name="audiobook_caption_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'mutagen>=1.45.1',
        'python-telegram-bot>=13.7',
        'python-dotenv>=0.19.0'
    ],
    author="Cerina",
    description="A tool to generate and upload captioned audiobooks to Telegram",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cerinawithasea/audiobook_caption_generator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'audiobook-caption=audiobook_caption_generator.cli:main',
        ],
    },
)

