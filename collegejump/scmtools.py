import re
import subprocess


def get_scm_version():
    """Collect the SCM version in setuptools-safe format."""
    try:
        description = subprocess.check_output(
            ['git', 'describe', '--always', '--dirty=.dirty']) \
            .decode('UTF-8').strip()
        version_data = re.match('''
                (?P<release>[0-9]+(\.[0-9]+)*) # Match the release version
                (
                    -(?P<dev>[0-9]+) # Match a since-last-tag number if present
                )?
                (
                    -g
                    (?P<git>[0-9a-f]+)   # Match the commit ID if present
                    (?P<dirty>\.dirty)?  # Match the "dirty" identifier if present
                )?
                ''',
                                description, re.VERBOSE)
        groups = {group: (value if value else '')
                  for group, value
                  in version_data.groupdict().items()}
        version = '{release}{dev_segment}{internal_segment}'.format(
            dev_segment='.dev' + groups['dev'] if groups['dev'] else '',
            internal_segment='+' + groups['git'] +
            groups['dirty'] if groups['git'] else '',
            **version_data.groupdict())

    except Exception as e:
        print("Could not get version: {}", repr(e))
        version = 'UNAVAILABLE'

    return version
