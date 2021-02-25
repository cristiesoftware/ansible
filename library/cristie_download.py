import requests
import json
import tempfile
from ansible.module_utils.basic import *


DOCUMENTATION = r'''
---
module: cristie_download

short_description: Downloads latest version of Cristie product from portal.cristie.com

version_added: "1.0.0"

description: This is my longer description explaining my test info module.

options:
    username:
        description: email address registered with portal.cristie.com
        required: true
        type: str
    password:
        description: password for portal.cristie.com
        required: true
        type: str
    product:
        description: Cristie product to install e.g.. cbmr, tbmr, abmr, clone, cobmr
        required: true
    platform:
        description: Type of platform you are using Linux, AIX, Solaris, Windows
        required: true
    package:
        description: which kind of package you want e.g. tar.gz, rpm, deb, exe
        required: true

author:
    - Cristie Software
'''

EXAMPLES = r'''
# Download CBMR for Linux
- name: Download latest CBMR
  cristie_download:
    product: cbmr
    username: user@company.co.uk
    password: Password
    platform: Linux
    package: rpm

# Download CBMR for Debain
- name: Download latest CBMR
  cristie_download:
    product: cbmr
    username: user@company.co.uk
    password: Password
    platform: Linux
    package: deb

# Download ABMR for Windows
- name: Download latest CBMR
  cristie_download:
    product: abmr
    username: user@company.co.uk
    password: Password
    platform: Windows
    package: exe

'''




class Portal:

    def __init__(self,  _module): 
        self.username =  _module.params['username']
        self.password =  _module.params['password']
        self.product =   _module.params['product']
        self.platform = _module.params['platform']
        self.package = _module.params['package']
        self.version = None
        self.api_url = "https://portal-staging.cristie.com/portal/v1"
        self.headers = {'Content-Type': 'application/json'}
        self.token = None
        self.am = _module
        self.get_auth_token()
        self.downloads = None
       

    def get_auth_token(self):
        url = self.api_url + "/login"
        payload = {
            "username": self.username,
            "password": self.password
        }
        try:
            auth = requests.post(url, data=json.dumps(payload), headers=self.headers)
        except requests.exceptions.HTTPError as errh:
            return self.am.fail_json(msg="HTTP ERROR", error=errh)
        except requests.exceptions.ConnectionError as errc:
            return self.am.fail_json(msg="CONNECTION ERROR", error=errc)
        except requests.exceptions.Timeout as errt:
            return self.am.fail_json(msg="TIMEOUT ERROR")
        except requests.exceptions.RequestException as err:
            return self.am.fail_json(msg="SOMETHING ELSE HAPPENED", error=err)
            
        if auth.status_code == 200:
            self.token = auth.json().get("token")
            self.headers.update({'Authorization': "Bearer " + self.token})
            return self.token
        return None

    def validate_username(self):
        """
        Check whether the username take the form of standard email address
        :return: bool.
        """
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"

        if re.search(email_regex, self.username):
            return True
        return False

    def list_downloads(self):
        url = self.api_url + "/downloads/list"
        try:
            downloads = requests.get(url, headers=self.headers)
        except requests.exceptions.HTTPError as errh:
            return self.am.fail_json(msg="Error getting download list, HTTP ERROR", error=errh)
        except requests.exceptions.ConnectionError as errc:
            return self.am.fail_json(msg="Error getting download list, CONNECTION ERROR", error=errc)
        except requests.exceptions.Timeout as errt:
            return self.am.fail_json(msg="Error getting download list, TIMEOUT ERROR",  error=errt)
        except requests.exceptions.RequestException as err:
            return self.am.fail_json(msg="Error getting download list, SOMETHING ELSE HAPPENED", error=err)
        if downloads.status_code == 200:
            self.downloads = downloads.json()
            return self.downloads
        return self.am.fail_json(msg="No Downloads found")

    def get_latest_download(self):  
        product = self.product
        downloads = self.list_downloads().get(product).get("latest")
        for download in downloads:
            installs = download.get("installs")
            for install in installs:
                url = install.get("url")
                if install.get("product") == self.product.upper() and install.get("platform") == self.platform and self.package in url:
                    return url
        return self.am.exit_json(msg="unable to find a suitable download for chosen options")

    def get_versioned_download(self):
        product = self.product
        downloads = self.list_downloads().get(product).get("archived")
        for download in downloads:
            installs = download.get("installs")
            for install in installs:
                url = install.get("url")
                if install.get("product") == self.product.upper() and install.get("platform") == self.platform and self.package in url \
                        and install.get("version") == self.version:
                    print(url)
                    return url
        return self.am.exit_json(msg="unable to find a suitable download for chosen options")

    def download_binary(self, url):
        filename = url.split('/')[-1]
        local_filename = tempfile.gettempdir() + "/" + filename
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
        except requests.exceptions.HTTPError as errh:
            return self.am.fail_json(msg="Download Failed, HTTP Error", error=errh)
        except requests.exceptions.ConnectionError as errc:
            return self.am.fail_json(msg="Download Failed, Connection Error", error=errc)
        except requests.exceptions.Timeout as errt:
            return self.am.fail_json(msg="Download Failed, Timeout Error", error=errt)
        except requests.exceptions.RequestException as err:
            return self.am.fail_json(msg="Download Failed, Unknown Error", error=err)
        return local_filename


def main():
    fields = {
        "username": {"default": None, "required": True, "type": str},
        "password": {"default": None, "required": True, "type": str},
        "product": {"required": True, "choices": ['abmr', 'cbmr', 'cobmr', 'tbmr', 'clone']},
         "platform": {"default": None, "required": True, "choices":['AIX','Linux','Solaris','Windows']},
        "package": {"default": None, "required": True, "choices":['deb','exe','rpm','tar.gz']},
        #"version": {"default": None, "required": False},
    }
    am = AnsibleModule(argument_spec=fields)
    portal = Portal(am)

    if not portal.validate_username():
        am.fail_json(changed=False, msg="Invalid username")

    if  portal.list_downloads():
        url = portal.get_latest_download()
        download = portal.download_binary(url)
        am.exit_json(changed=True,msg="Successfully Downloaded package ", filename=download)
    else:
        am.fail_json(changed=False, msg="Error Downloading package")

main()