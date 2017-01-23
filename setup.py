import os
import shutil
from distutils.core import setup

from setuptools import find_packages

package_name = "peek-worker"
package_version = '0.0.9'

egg_info = "%s.egg-info" % package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

setup(
    name=package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    entry_points={
        'console_scripts': [
            'run_peek_worker = peek_worker.run_peek_worker.main',
        ],
    },
    install_requires=["peek-platform"],
    version=package_version,
    description='Peek Platform - Worker Service',
    author='Synerty',
    author_email='contact@synerty.com',
    url='https://github.com/Synerty/%s' % package_name,
    download_url='https://github.com/Synerty/%s/tarball/%s' % (
        package_name, package_version),
    keywords=['Peek', 'Python', 'Platform', 'synerty'],
    classifiers=[
        "Programming Language :: Python :: 3.5",
    ],
)
