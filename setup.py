import os
import pkg_resources
import setuptools

setuptools.setup(
    name='whisper_server',
    version='0.0.1',
    author='Nicholas Albion',
    python_requires=">=3.10",
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    entry_points={
        'console_scripts': [
            # 'whisper_server=whisper_server.app:main',
            'whisper_server=whisper_server.__main__:main',
        ]
    }
)
