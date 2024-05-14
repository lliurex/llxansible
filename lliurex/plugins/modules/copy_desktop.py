#!/usr/bin/python3

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: copy_desktop

short_description: This is my test module

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is my longer description explaining my test module.

options:
    name:
        description: This is the desired desktop file
        required: true
        type: str
    user:
        description:
            - User for adding desktop file
            - Parameter description can be a list as well.
        required: false
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Pass in a message
- name: Add zero-center to desktop for all users
  llx.lliurex.copy_desktop:
    name: zero-center

# pass in a message and have changed true
- name: Add zero-center to user lliurex
  llx.lliurex.copy_desktop:
    name: zero-center
    user: lliurex

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'zero-center'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'done'
'''

from ansible.module_utils.basic import AnsibleModule

import subprocess
import os
import pwd

def add_desktop(name, user='all'):
    
    def add_desktop_user(filename,user):
        dirname=subprocess.check_output(f"su {user} -l -c 'xdg-user-dir DESKTOP' -s /bin/bash",shell=True,stderr=subprocess.STDOUT)
        try:
            dirname=dirname.decode()
        except:
            pass
        dirname=dirname.strip()
        if not dirname or not os.path.isdir(dirname):
            raise Exception(f'Can\'t get {user} home')
        outmsg = subprocess.check_output(f"cp {filename} {dirname}",shell=True,stderr=subprocess.STDOUT)
        return f'{user}'
    
    created = []
    try:
        filename='/usr/share/applications/'+name
        if not os.path.isfile(filename):
            raise Exception(f'File {filename} not available')
        if user != 'all':
            try:
                add_desktop_user(filename,user)
                created.append(f'{user} completed')
            except Exception as e:
                created.append(f'{user} failed, {e}')
        else:
            out = []
            for us in (x.pw_name for x in pwd.getpwall()):
                try:
                    add_desktop_user(filename,us)
                    created.append(f'{us} completed')
                except Exception as e:
                    created.append(f'{us} failed, {e}')
        return created
    except Exception as e:
        raise Exception(e)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        user=dict(type='str', required=False, default=False)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # Run actions
    changed = False
    error = False
    try:
        msgs=add_desktop(module.params['name'],module.params['user'])
        for msg in msgs:
            if 'failed' in msg:
                error = True
                break
            if 'completed' in msg:
                changed = True
                break
    except Exception as e:
        msgs=[str(e)]
        error = True

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['original_message'] = f"{module.params['name']} {module.params['user']}"
    result['message'] = '\n'.join(msgs)

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    result['changed'] = changed

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if error:
        # module.fail_json(msg='Error', **result)
        module.fail_json(msg='\n'.join(msgs), **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()