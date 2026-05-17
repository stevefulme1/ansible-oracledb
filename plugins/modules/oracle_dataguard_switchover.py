#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Steve Fulmer
# Apache-2.0 (see LICENSE)
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""oracle_dataguard_switchover module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r"""
---
module: oracle_dataguard_switchover
short_description: Execute Data Guard switchover/failover
description:
    - Execute Data Guard switchover/failover.
version_added: "1.0.0"
author:
    - Steve Fulmer (@stevefulme1)
options:
    state:
        description: Desired state of the resource.
        type: str
        default: present
        choices: [present, absent]
    host:
        description: API host address.
        type: str
        required: true
    switchover_id:
        description: Unique identifier of the dg switchover.
        type: str
    name:
        description: Display name.
        type: str
    username:
        description: Authentication username.
        type: str
    password:
        description: Authentication password.
        type: str
    api_key:
        description: API key for authentication.
        type: str
    validate_certs:
        description: Validate SSL certificates.
        type: bool
        default: true
"""

EXAMPLES = r"""
- name: Create a dg switchover
  stevefulme1.oracledb.oracle_dataguard_switchover:
    host: api.example.com
    name: my-dg-switchover
    state: present

- name: Delete a dg switchover
  stevefulme1.oracledb.oracle_dataguard_switchover:
    host: api.example.com
    switchover_id: "example-id"
    state: absent
"""

RETURN = r"""
dg_switchover:
    description: Resource details.
    returned: on success
    type: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.stevefulme1.oracledb.plugins.module_utils.api_client import ApiClient
    HAS_CLIENT = True
except ImportError:
    HAS_CLIENT = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type="str", default="present", choices=["present", "absent"]),
            switchover_id=dict(type="str"),
            name=dict(type="str"),
            host=dict(type="str", required=True),
            username=dict(type="str"),
            password=dict(type="str", no_log=True),
            api_key=dict(type="str", no_log=True),
            validate_certs=dict(type="bool", default=True),
        ),
        supports_check_mode=True,
        required_if=[("state", "absent", ("switchover_id",))],
    )

    if not HAS_CLIENT:
        module.fail_json(msg="Required Python libraries not found.")

    client = ApiClient(module)
    state = module.params["state"]
    resource_id = module.params.get("switchover_id")

    if state == "present":
        existing = None
        if resource_id:
            existing = client.get("dg_switchover", resource_id)
        elif module.params.get("name"):
            candidates = client.list("dg_switchover", {dict(name=module.params.get("name", ""))})
            if candidates:
                existing = candidates[0]

        if existing:
            if module.check_mode:
                module.exit_json(changed=False, dg_switchover=existing)
            result = client.update("dg_switchover", resource_id or existing.get("id", ""), module.params)
            module.exit_json(changed=True, dg_switchover=result)
        else:
            if module.check_mode:
                module.exit_json(changed=True)
            result = client.create("dg_switchover", module.params)
            module.exit_json(changed=True, dg_switchover=result)
    else:
        existing = None
        if resource_id:
            existing = client.get("dg_switchover", resource_id)
        if not existing:
            module.exit_json(changed=False)
        if module.check_mode:
            module.exit_json(changed=True)
        client.delete("dg_switchover", resource_id)
        module.exit_json(changed=True)


if __name__ == "__main__":
    main()
