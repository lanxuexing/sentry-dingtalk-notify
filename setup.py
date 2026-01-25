from setuptools import setup, find_packages

setup(
    name='sentry-dingtalk-notify',
    version='1.0.0',
    author='lanxuexing',
    author_email='your.email@example.com',
    url='https://github.com/lanxuexing/sentry-dingtalk-notify',
    description='A Sentry plugin for sending notifications to DingTalk (DingDing).',
    long_description=open('README.md').read(),
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'sentry>=9.0.0',
        'requests',
    ],
    entry_points={
        'sentry.plugins': [
            'dingtalk_notify = sentry_dingtalk_notify.plugin:DingTalkPlugin',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
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
        'Framework :: Django',
    ],
)
