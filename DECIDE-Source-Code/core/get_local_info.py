from os import system
import platform
import subprocess
import sys
import re
import json
from utils.utils import ignore_comment
from packaging.requirements import Requirement

VERSION_PATTERN = r'\d+\.(?:\d+\.)*\d+'
ERROR = 'error'

def catch_version(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode == 0:
        return res.stdout.decode().strip()
    else:
        return ERROR

class LocalInformation(object):
    def __init__(self, mode, local_file_path=None):
        if mode == 'file':
            f = open(local_file_path, 'r')
            self.info = json.load(f)
            return
        elif mode == 'local':
            sys_name, sys_version = self.get_system_info()
            self.info = {
                "library": {
                    
                    'bazel': self.get_bazel_version(),
                    'gcc': self.get_gcc_version(),
                    'glibc': self.get_glibc_version()
                },
                "driver": {
                    'cuda': self.get_cuda_version(),
                    'cudnn': self.get_cuDNN_version()
                },
                "runtime": {
                    'python': self.get_python_version(),
                },
                "operating_system": {
                    sys_name: sys_version,
                    'conda': self.get_conda_version(),
                    'virtualenv': self.get_virtualenv_version()
                },
                "hardware": {
                    'bit': self.get_bitness()
                }
            }
            conda_lib = self.get_conda_env_packages()
            pip_lib = self.get_pip_env_packages()

            self.info['library'].update(pip_lib)
            self.info['library'].update(conda_lib)
            
            self.info['runtime']['python'] = '3.6'

    # python version
    def get_python_version(self):
        py_version = platform.python_version()
        v_list = py_version.split('.')
        if len(v_list) >= 2:
            py_ver = v_list[0] + '.' + v_list[1]
        else:
            py_ver = py_version
        return py_ver

    # conda version
    def get_conda_version(self):
        conda_cmd = 'conda --version'
        cv_res = catch_version(conda_cmd)
        if cv_res == ERROR:
            print('conda not found')
            return ''
        elif cv_res != '':
            return cv_res.split()[1]
        else:
            print('error in conda version')
            return ''
    
    # conda version
    def get_bazel_version(self):
        conda_cmd = 'bazel --version'
        cv_res = catch_version(conda_cmd)
        if cv_res == ERROR:
            print('bazel not found')
            return ''
        elif cv_res != '':
            return cv_res.split()[1]
        else:
            print('error in bazel version')
            return ''
        
    # virtualenv version
    def get_virtualenv_version(self):
        virtualenv_cmd = 'virtualenv --version'
        prefix = getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

        if prefix != sys.prefix:
            return ''
        else:
            cv_res = catch_version(virtualenv_cmd)
            if cv_res == ERROR:
                print('Not in virtualenv')
                return ''
            elif cv_res != '':
                return cv_res.split()[1]
            else:
                print('error in virtualenv version')
                return ''

    # jupyter version
    def get_jupyter_version(self):
        jupyter_cmd = 'jupyter --version'
        cv_res = catch_version(jupyter_cmd)

        res = {}
        if cv_res == ERROR:
            print('jupyter not installed!')
            return ''
        elif cv_res != '':
            jupyter_version = cv_res.split('\n')
            for jv in jupyter_version:
                if ':' in jv:
                    tmp = jv.split(':')
                    res[tmp[0].strip()] = tmp[1].strip()
            return res
        else:
            print('error in jupyter')
            return ''
        
    # gcc/g++ version
    def get_gcc_version(self):
        res = platform.python_compiler()
        if res == '':
            print('error in finding python complier')
            return ''
        gcc_version = re.search(VERSION_PATTERN, res).group(0)
        
        return gcc_version

    # python compiler
    def get_python_complier(self):
        res = platform.python_compiler()
        return res

    # glibc version
    def get_glibc_version(self):
        glibc_cmd = 'ldd --version'
        cv_res = catch_version(glibc_cmd)
        if cv_res == ERROR:
            print('Glibc not found!')
            return ''
        elif cv_res != '':
            tmp = cv_res.split('\n')
            glibc_version = re.search(VERSION_PATTERN, tmp[0]).group(0)
            return glibc_version
        else:
            print('error in glibc version')
            return ''

    # environmental packages (conda)
    def get_conda_env_packages(self):
        status = subprocess.run(f'conda list -e --json', shell=True, capture_output=True)
        conda_res = json.loads(status.stdout.decode())
        package_info = {}
        if status.returncode == 0:
            for item in conda_res:
                package_info[item['name'].lower()] = item['version']
            return package_info
        else:
            print('error')
            return {}

    # environmental packages (pip)
    def get_pip_env_packages(self):
        status = subprocess.run(f'pip freeze --all', shell=True, capture_output=True)
        package_info = {}
        if status.returncode == 0:
            pip_lib_list = status.stdout.decode().strip().split('\n')
            for pip_lib in pip_lib_list:
                pip_lib_str = ignore_comment(pip_lib)
                if pip_lib_str == '':
                    continue
                item = Requirement(pip_lib)
                if len(item.specifier) == 0:
                    version = ''
                elif len(item.specifier) == 1:
                    for sp in item.specifier:
                        version = str(sp.version)
                else:
                    print('error in pip local package: ', item)
                package_info[item.name.lower()] = version
            return package_info

        else:
            print('error')
            return []

    # system bitness
    def get_bitness(self):
        _32BIT = 2**31 - 1
        _64BIT = 2**63 - 1
        if sys.maxsize == _32BIT:
            return '32-bit'
        elif sys.maxsize == _64BIT:
            return '64-bit'
        else:
            return 'unknown'

    # platform information
    def get_system_info(self):
        uanme_res = platform.uname()
        version_str = uanme_res.version
        temp = version_str.split()[0]
        # temp = '#138~18.04.1-Ubuntu'
        sys_name = temp.split('-')[1].lower()
        sys_version = temp.split('-')[0].split('~')[1]
        # sys_version = '18.04'
        return sys_name, sys_version
    
    # cpu machine
    def get_cpu_arch(self):
        print(platform.machine())
        input()
        return {'machine': platform.machine(), 'processor': platform.processor()}

    # cuda version
    def get_cuda_version(self):
        cuda_version = ''
        platform = sys.platform
        if platform == 'linux': 
            nvidia_res = subprocess.run('nvidia-smi', shell=True, capture_output=True)
            if nvidia_res.returncode == 0:
                pattern = r'CUDA Version: \d+\.(?:\d+\.)*\d+'
                cuda_version = re.search(pattern, nvidia_res.stdout.decode()).group(0)
                res = cuda_version.split(': ')[1]
            else:
                nvcc_res = subprocess.getstatusoutput('nvcc --version')
                if nvcc_res[0] == 0:
                    # todo: extract version number from cuda_version
                    cuda_version = re.search(VERSION_PATTERN, nvcc_res[1]).group(0)
                    res = cuda_version
        elif platform == 'windows':
            pass
        return res

    # cuDNN version
    def get_cuDNN_version(self):
        platform = sys.platform
        res = ''
        if platform == 'linux': 
            cuDNN_sh = [
                'cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2', 
                'cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2'
            ]
            for c_sh in cuDNN_sh:
                cuDNN_res = subprocess.run(c_sh, shell=True, capture_output=True)
                if cuDNN_res.returncode == 0:
                    tmp = cuDNN_res.stdout.decode()
                    t_list = tmp.strip().split('\n')
                    version = []
                    for t in t_list:
                        version.append(t.split()[-1])
                    res = '.'.join(version)
                    break
                else:
                    continue
            
            if res == '':
                print('cuDNN not found!')

        elif platform == 'windows':
            pass
        return res
    
    
    def get_info(self):
        return self.info