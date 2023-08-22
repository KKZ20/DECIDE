import re
from config.library import COMPONENT_LIST

LIBRARY_PATTERN = '|'.join(COMPONENT_LIST)

version_pattern1 = r'((\s|\()(v|ver|r){0,1}((\d{1,2})(\.\d{1,3})(\.\d{1,3}){0,1}))'
version_pattern2 = r'((\s|\()(v|ver|r){0,1}((\d{1,2})(\.x)(\.x){0,1}))'
version_pattern3 = r'((\s|\()(v|ver|r){0,1}((\d{1,2})(\.\d{1,3})(\.x)))'
version_pattern4 = f'(({LIBRARY_PATTERN})' + r'(,){0,1}\s*(version(s){0,1}){0,1}\s*(from){0,1}\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.\d{1,3}){0,1}\s*(to|and|or|–|-)\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.\d{1,3}){0,1})'
version_pattern5 = f'(({LIBRARY_PATTERN})' + r'(,){0,1}\s*(version(s){0,1}){0,1}\s*(from){0,1}\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.x){0,1}\s*(to|and|or|–|-)\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.x){0,1})'
version_pattern6 = f'(({LIBRARY_PATTERN})' + r'(,){0,1}\s*(version(s){0,1}){0,1}\s*(is|to){0,1}\s*(\(){0,1}\s*(>=|<=|==|>|<|=|~=|-){0,1}\s*(higher than|lower than|later than|earlier than|still){0,1}\s*(,){0,1}\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.\d{1,3}){0,1})'
version_pattern7 = f'(({LIBRARY_PATTERN})' + r'(,){0,1}\s*(version(s){0,1}){0,1}\s*(is|to){0,1}\s*(\(){0,1}\s*(>=|<=|==|>|<|=|~=|-){0,1}\s*(higher than|lower than|later than|earlier than|still){0,1}\s*(,){0,1}\s*(v|ver){0,1}\s*(\d{1,2})(\.\d{1,3}){0,1}(\.x){0,1})'


ONLY_VERSION_PATTERN = [re.compile(version_pattern1), re.compile(version_pattern2), re.compile(version_pattern3)]
NAME_WITH_VERSION_PATTERN = [re.compile(version_pattern4), re.compile(version_pattern5), re.compile(version_pattern6), re.compile(version_pattern7)]

PATH_PATTERN = re.compile(r'\S*((\/|\\){1}\S*)')
IP_ADDRESS_PATTERN = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')
TIME_PATTERN = re.compile(r'\d{2}:\d{2}:\d{2}')
TIME_PATTERN_2 = re.compile(r'\d+(\.\d+){0,1}\s*(sec|second|seconds|SEC|SECOND|SECONDS|min|minute|minutes|MIN|MINUTE|MINUTES|hr|hour|hours|HR|HOUR|HOURS|day|days|DAY|DAYS|week|weeks|WEEK|WEEKS|month|months|MONTH|MONTHS|year|years|YEAR|YEARS)')
TIME_PATTERN_3 = re.compile(r'\d+(\.\d+){0,1}(s|S|H|h)')
MEMORY_PATTERN = re.compile(r'\d+(\.\d+){0,1}(\s|-){0,1}(KB|MB|GB|TB|kb|mb|gb|tb|bit|BIT|byte|BYTE|bytes|BYTES)')
MEMORY_PATTERN_2 = re.compile(r'\d+(\.\d+){0,1}(K|G|M|T|k|m|g|t|b|B)')
ENCODE_PATTERN = re.compile(r'(utf|UTF|iso|ISO)(-){0,1}(\d{1,3})((-){0,1}(\d{1,3})){0,1}')
FILENAME_PATTERN = re.compile(r'((\S+)(\.[a-zA-Z]+))')

VERSION_PATTERN = re.compile(r'((\d{1,2})(\.\d{1,3}){0,1}(\.\d{1,3}){0,1})')