# ملف: setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="APIs",
    version="0.1.0",
    author="osamh64",
    author_email="osamh123451191@gmail.com",
    description="مكتبة للتبديل التلقائي بين خدمات API متعددة مع آلية إعادة المحاولة",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/osamh64/APIs",
    project_urls={
        "Bug Tracker": "https://github.com/osamh64/APIs/issues",
        "Source Code": "https://github.com/osamh64/APIs",
        "Documentation": "https://github.com/osamh64/APIs/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
)