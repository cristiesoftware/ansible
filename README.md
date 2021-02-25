# Ansible
Ansible libraries for deployment and licensing of Cristie products.

This consists of two modules:

# cristie_license

Licenses a Cristie Product either via the portal or offline

Options:

- username:
  - description: Email address registered with portal.cristie.com (needed for online activation only)
  - required: false
  - type: str
- password:
  - description: Password for portal.cristie.com (needed for online activation only)
  - required: false
  - type: str
- product:
  - description: Cristie product to install e.g.. abmr, cbmr, cobmr, clone, nbmr, tbmr
  - required: true
    
- contract_code:
  - description: Contract Code in the form of XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX (for online activation)
  - required: false
    
- act_code:
  - description: Activation Code in the form of XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX for offline activation
  - required: false
    
- request_sig:
  - description: Machine signiture
  - required: false
    
- licmgr_path:
  - description: Path to license manager binary
  - required: false
        
# cristie_download

Downloads latest version of Cristie product from portal.cristie.com

Options:

- username:
  - description: Email address registered with portal.cristie.com
  - required: true
  - type: str
- password:
  - description: Password for portal.cristie.com
  - required: true
  - type: str
- product:
  - description: Cristie product to install e.g.. abmr, cbmr, cobmr, clone, nbmr, tbmr
  - required: true
- platform:
  - description: Type of platform you are using Linux, AIX, Solaris, Windows
  - required: true
- package:
  - description: Which kind of package you want e.g. tar.gz, rpm, deb, exe
  - required: true  
