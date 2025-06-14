# setup.py
from setuptools import setup, find_packages

setup(
    name='botsh',
    version='0.1.0',
    description='CLI LLM Agent for terminal-based AI interaction',
    author='你的名字',
    packages=find_packages(),
    install_requires=[
        'openai',
        'prompt_toolkit',
        # 如果有别的依赖也加上
    ],
    entry_points={
        'console_scripts': [
            'ag=botsh.__main__:main',  # 绑定 ag 命令到 main()
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
