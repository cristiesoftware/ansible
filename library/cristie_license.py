#!/usr/bin/python

import re
import os.path
import traceback
from ansible.module_utils.basic import *
DOCUMENTATION = r'''
---
module: cristie_license

short_description: License a Cristie product either offline or online

version_added: "1.0.0"

description: Licenses a Cristie Product either via the portal or offline
options:
    username:
        description: email address registered with portal.cristie.com (needed for online activation only)
        required: false
        type: str
    password:
        description: password for portal.cristie.com (needed for online activation only)
        required: false
        type: str
    product:
        description: Cristie product to install e.g.. cbmr, tbmr, abmr, clone, cobmr
        required: true
    contract_code:
        description: Contract Code in the form of XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX (for online activation)
        required: false
    act_code:
        description: Activation Code in the form of XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX for offline activation
        required: false
    request_sig:
        description: MAchine signiture
        required: false
    licmgr_path:
        description: path to license mgr 
        required: false

author:
    - Cristie Software
'''

EXAMPLES = r'''
# Activate CBMR online
- name: Activate CBMR
  cristie_license:
    product: cbmr
    username: user@company.co.uk
    password: Password
    contract_code: XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX

# Activate CBMR offline
- name: Download latest CBMR
  cristie_license:
    product: cbmr
    activation_code: XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX


'''

class cristie_license:

    def __init__(self, _module):
        self.module = _module
        self.username  = _module.params['username']
        self.password = _module.params['password']
        self.product = _module.params['product']
        self.contract = _module.params['contract_code']
        self.act_code = _module.params['act_code']
        self.request_sig = _module.params['request_sig']
        self.licmgr_path = _module.params['licmgr_path']
        self.licence = None

    def activate(self):
        """
        Determines whether to activate license using the online method or to use offline method.
        :return: bool: Success or failed, Additional information.
        """

        self.licence = self.get_license_status()

        # Online activation
        if self.username and self.password and self.contract:
            return self.online_activation()

        # Offline activation
        if self.act_code:
            return self.offline_activation()

        # Exit early if a username and Password is supplied but not contract
        if self.username and self.password and not self.act_code and not self.contract:
            self.module.fail_json(msg="Online Activation: Contract code empty or not supplied")

        # Catch all exit early.
        self.module.fail_json(msg="Unable to determine activation type please please a activation code or username, password and contract code")


    def  validate_online_fields(self):
        """
        checks the username contains an email address and the activation code follows the expected format.
        :rtype: object { status: bool, message with additional detail }
        """
        if not self.validate_username():
            self.module.fail_json(msg="Please ensure username contains an email address")

        if not self.validate_code(self.contract):
            self.module.fail_json(msg="Invalid contract code format. Use XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX")

        return True

    def get_license_status(self):
        if not os.path.isfile(self.licmgr_path):
            self.module.fail_json(msg="Unable to find licmgr. Please check the path is correct.")
        command = [self.licmgr_path, "-p", self.product]
        rc, stdout, stderr = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json("Error getting license status", meta=stdout)
        if re.search("Trial licence",stdout):
            return "Trial license"
        if re.search("Full licence",stdout):
            return "Trial license"
        self.module.fail_json("Unknown License Status", meta=stdout)



    def validate_username(self):
        """
        Check whether the username take the form of standard email address
        :return: bool.
        """
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if re.search(email_regex, self.username):
            return True
        return False

    def validate_code(self,code):
        """
        Validate Activation code or Contract Code in the form of XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX
        :param code: Activation/Contract code
        :return: bool
        """
        act_code_regex = "[A-Za-z0-9]{8}\\-[A-Za-z0-9]{8}\\-[A-Za-z0-9]{8}\\-[A-Za-z0-9]{8}$"
        if re.search(act_code_regex, code):
            return True
        return False

    def online_activation(self):
            self.validate_online_fields()
            self.activate_product_online()


    def activate_product_online(self):
        command = [self.licmgr_path,"-p", self.product.upper(), "--cid", self.contract]
        rc, stdout, stderr = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json("Error Activating product", meta=stdout)

    # stage 2
        command = [self.licmgr_path, "-p", self.product]
        if self.username and self.password:
            command = command + ["--cred", self.username + "," + self.password]
        rc, stdout, stderr = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json("Error Activating product", meta=stdout)
        changed = False
        if self.get_license_status() != self.licence:
            changed = True
        return {"changed": changed, "msg": "Successfully licensed " + self.product}

    def offline_activation(self):
        if not self.validate_code(self.act_code)
            self.mdoule.fail_json("Invalid Activation Code Format.")
        command = [self.licmgr_path, "-p", self.product,"--act",self.act_code]
        rc, stdout, stderr = self.module.run_command(command)
        if rc != 0:
            self.module.fail_json("Error Activating product", meta=stdout)
        changed = False
        if self.get_license_status() != self.licence:
            changed = True
        return {"changed": changed, "msg": "Successfully licensed " + self.product}

def main ():
    fields = {
        "username": {"default": None, "required": False, "type": str},
        "password": {"default": None, "required": False, "type": str},
        "product": {"required": True, "choices": ['abmr', 'cbmr', 'cobmr', 'tbmr', 'clone']},
        "contract_code": {"default": None, "required": False, "type": str},
        "act_code": {"default": None, "required": False, "type": str},
        "request_sig": {"default": False, "type": bool},
        "licmgr_path": {"default": "/usr/bin/licmgr","required": False, "type":str}
    }
    module = AnsibleModule(argument_spec=fields)
    licmgr = cristie_license(module)
    activation = licmgr.activate()
    module.exit_json(changed=activation.get("changed"), meta=activation)


if __name__ == '__main__':
    main()

