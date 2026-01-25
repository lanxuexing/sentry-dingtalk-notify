import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'sentry_dingtalk_notify', '__version__.py')) as f:
    exec(f.read(), about)

setup(
    name='sentry-dingtalk-notify',
    version=about['__version__'],
    author='lanxuexing',
    author_email='lanxuexing313wsr@163.com',
    url='https://github.com/lanxuexing/sentry-dingtalk-notify',
    description='A sentry extension integrates DingTalk robot webhook',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
    ],
    entry_points={
        'sentry.plugins': [
            'sentry_dingtalk_notify = sentry_dingtalk_notify.plugin:DingTalkPlugin',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: Django',
    ],
)
