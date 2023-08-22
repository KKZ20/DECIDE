import argparse
import json
from core.module_parser import ModuleParser
from core.get_local_info import LocalInformation
from core.get_requirement_info import *
from core.neo4j import neo4j_connect
from core.detect import detect_version_issue

parser = argparse.ArgumentParser(description='This is a dependency issue detector for python project.')
parser.add_argument('-n', '--name', required=True, help="The target DL project to be tested.")
parser.add_argument('-m', '--mode', default='file', choices=['file', 'local'], help="The source of aquiring local information.")
parser.add_argument('-l', '--local', default=None, help="The path of local stack information file")
parser.add_argument('-r', '--requirements', default=None, help="The path of project's requirements.txt file")
parser.add_argument('-p', '--project', default=None, help="The root path of the target project.")

def main():
    # reading arguments
    args = parser.parse_args()
    req_file_path = f'./experiment/{args.name}/requirements.txt'
    local_file_path = f'./experiment/{args.name}/local_info.json'

    if args.requirements is not None:
        req_file_path = args.requirements
    if args.local is not None:
        local_file_path = args.local

    # get requirements information or project declared requirements
    req_stack = requirements_info(req_file_path)

    if args.project is not None:
        module_parser = ModuleParser(args.project)
        proj_module, proj_api = module_parser.parse()
        project_lib = filter_using_module(proj_module)
        res = combine_requirement_info(req_stack, project_lib)
        req_stack = res

    # get local information
    local_stack = LocalInformation(args.mode, local_file_path).get_info()

    # connect to neo4j
    graph = neo4j_connect()

    if graph is None:
        print('Failed to connect to the knowledge base.')
        return
    else:
        print('Successfully connected to the knowledge base.')

    detect_version_issue(local_stack, req_stack, graph)

    return


if __name__ == '__main__':
    main()