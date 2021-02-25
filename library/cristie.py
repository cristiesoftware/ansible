#!/usr/bin/python

from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
from ansible.module_utils.yumdnf import *
import requests
api_url = "https://portal-staging.cristie.com/portal/v1"


def main():
    fields = {
        "product": {"required": True, "type": "str", "choices": ['ABMR', 'CBMR', 'CoBMR', 'TBMR']},
        "contract": {"required": True, "type": "str", "default": None},
        "username": {"required": False, "type": "str", "default": None},
        "password": {"required": False, "type": "str", "no_log": True, "default": None},
        "license_code": {"required": False, "type": "str", "default": None},
        "offline": {"required": False, "type": "bool", "default": False},
    }

    module = AnsibleModule(argument_spec=fields)
    response = {"hello": "world"}
    module.exit_json(changed=False, meta=module.params)


    




if __name__ == '__main__':
    main()

