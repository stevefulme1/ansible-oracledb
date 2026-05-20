# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

try:
    import oracledb

    HAS_ORACLEDB = True
    ORACLEDB_IMPORT_ERROR = None
except ImportError as e:
    HAS_ORACLEDB = False
    ORACLEDB_IMPORT_ERROR = str(e)

# Map string mode names to oracledb constants
_MODE_MAP = {
    "sysdba": "AUTH_MODE_SYSDBA",
    "sysoper": "AUTH_MODE_SYSOPER",
    "normal": "AUTH_MODE_DEFAULT",
}


def oracledb_argument_spec():
    """Return the common argument spec for Oracle DB modules."""
    return dict(
        oracle_host=dict(type="str", default="localhost"),
        oracle_port=dict(type="int", default=1521),
        oracle_user=dict(type="str", required=True),
        oracle_password=dict(type="str", required=True, no_log=True),
        oracle_service_name=dict(type="str"),
        oracle_sid=dict(type="str"),
        oracle_mode=dict(
            type="str", choices=["sysdba", "sysoper", "normal"], default="normal"
        ),
        oracle_thick_mode=dict(type="bool", default=False),
        oracle_thick_lib_dir=dict(type="str"),
    )


class OracleDBClient(object):
    """Wrapper around python-oracledb for Ansible modules."""

    def __init__(self, module):
        """Initialize Oracle DB client from Ansible module params.

        Args:
            module: AnsibleModule instance with Oracle connection parameters.
        """
        self.module = module
        self.conn = None
        self._cursor = None

        if not HAS_ORACLEDB:
            module.fail_json(
                msg="python-oracledb is required: pip install oracledb. "
                "Import error: %s" % ORACLEDB_IMPORT_ERROR
            )

        self._connect()

    def _connect(self):
        """Establish connection to Oracle database."""
        params = self.module.params
        host = params["oracle_host"]
        port = params["oracle_port"]
        user = params["oracle_user"]
        password = params["oracle_password"]
        service_name = params.get("oracle_service_name")
        sid = params.get("oracle_sid")
        mode_str = params.get("oracle_mode", "normal")
        thick_mode = params.get("oracle_thick_mode", False)
        thick_lib_dir = params.get("oracle_thick_lib_dir")

        if thick_mode:
            oracledb.init_oracle_client(lib_dir=thick_lib_dir)

        # Build DSN
        if service_name:
            dsn = oracledb.makedsn(host, port, service_name=service_name)
        elif sid:
            dsn = oracledb.makedsn(host, port, sid=sid)
        else:
            self.module.fail_json(
                msg="Either oracle_service_name or oracle_sid must be provided."
            )

        # Resolve connection mode
        mode_attr = _MODE_MAP.get(mode_str, "AUTH_MODE_DEFAULT")
        auth_mode = getattr(oracledb, mode_attr, 0)

        try:
            self.conn = oracledb.connect(
                user=user, password=password, dsn=dsn, mode=auth_mode
            )
        except oracledb.Error as exc:
            self.module.fail_json(msg="Oracle connection failed: %s" % str(exc))

    @property
    def cursor(self):
        """Return a reusable cursor."""
        if self._cursor is None or self._cursor.connection is None:
            self._cursor = self.conn.cursor()
        return self._cursor

    def execute(self, sql, params=None):
        """Execute a SQL statement.

        Args:
            sql: SQL statement string.
            params: Optional bind parameters (list or dict).

        Returns:
            The cursor after execution.
        """
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return self.cursor
        except oracledb.Error as exc:
            self.module.fail_json(
                msg="SQL execution failed: %s" % str(exc), sql=sql
            )

    def fetchone(self, sql, params=None):
        """Execute SQL and return one row.

        Args:
            sql: SQL query string.
            params: Optional bind parameters.

        Returns:
            A single row tuple or None.
        """
        self.execute(sql, params)
        return self.cursor.fetchone()

    def fetchall(self, sql, params=None):
        """Execute SQL and return all rows.

        Args:
            sql: SQL query string.
            params: Optional bind parameters.

        Returns:
            List of row tuples.
        """
        self.execute(sql, params)
        return self.cursor.fetchall()

    def fetchall_as_dicts(self, sql, params=None):
        """Execute SQL and return rows as list of dicts.

        Args:
            sql: SQL query string.
            params: Optional bind parameters.

        Returns:
            List of dicts with column names as keys.
        """
        self.execute(sql, params)
        columns = [col[0].lower() for col in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def close(self):
        """Close cursor and connection."""
        if self._cursor:
            try:
                self._cursor.close()
            except Exception:
                pass
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
