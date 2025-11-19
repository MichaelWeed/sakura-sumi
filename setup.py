"""Setup configuration for 🌸 Sakura Sumi - OCR Compression System."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name='ocr-compression',
    version='1.0.0',
    description='🌸 Sakura Sumi - OCR Compression System - Convert codebases to compressed PDFs for LLM analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sakura Sumi Contributors',
    author_email='',
    url='https://github.com/yourusername/ocr-compression',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ocr-compress=src.main:main',
            'ocr-web=scripts.run_web:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
)

