# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  oracle_host:
    description:
      - Hostname or IP address of the Oracle database server.
    type: str
    default: localhost
  oracle_port:
    description:
      - Listener port of the Oracle database.
    type: int
    default: 1521
  oracle_user:
    description:
      - Username for Oracle database authentication.
    type: str
    required: true
  oracle_password:
    description:
      - Password for Oracle database authentication.
    type: str
    required: true
  oracle_service_name:
    description:
      - Oracle service name to connect to.
      - Mutually exclusive with O(oracle_sid).
    type: str
  oracle_sid:
    description:
      - Oracle SID to connect to.
      - Mutually exclusive with O(oracle_service_name).
    type: str
  oracle_mode:
    description:
      - Connection mode for Oracle database.
      - Use V(sysdba) for administrative operations.
      - Use V(sysoper) for operator-level operations.
      - Use V(normal) for standard connections.
    type: str
    choices: [sysdba, sysoper, normal]
    default: normal
  oracle_thick_mode:
    description:
      - Whether to use Oracle thick mode (requires Oracle Client libraries).
      - Thick mode is needed for some features like external authentication.
    type: bool
    default: false
  oracle_thick_lib_dir:
    description:
      - Path to Oracle Client libraries for thick mode.
      - Only used when O(oracle_thick_mode=true).
    type: str
"""
