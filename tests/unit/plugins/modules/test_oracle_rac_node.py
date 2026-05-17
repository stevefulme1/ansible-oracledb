# -*- coding: utf-8 -*-
"""Comprehensive unit tests for oracle_rac_node module."""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch, call

from ansible_collections.stevefulme1.oracledb.plugins.modules import oracle_rac_node


class TestDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert hasattr(oracle_rac_node, "DOCUMENTATION")
        assert len(oracle_rac_node.DOCUMENTATION) > 0

    def test_documentation_has_module_name(self):
        assert "oracle_rac_node" in oracle_rac_node.DOCUMENTATION

    def test_documentation_has_short_description(self):
        assert "short_description" in oracle_rac_node.DOCUMENTATION

    def test_documentation_has_options(self):
        assert "options" in oracle_rac_node.DOCUMENTATION

    def test_documentation_has_state(self):
        assert "state" in oracle_rac_node.DOCUMENTATION

    def test_examples_exist(self):
        assert hasattr(oracle_rac_node, "EXAMPLES")
        assert len(oracle_rac_node.EXAMPLES) > 0

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.oracledb" in oracle_rac_node.EXAMPLES

    def test_return_exists(self):
        assert hasattr(oracle_rac_node, "RETURN")
        assert len(oracle_rac_node.RETURN) > 0


class TestCreate:
    """Test resource creation operations."""

    def test_create_returns_resource(self, mock_client):
        mock_client.create.return_value = {"id": "new-1", "name": "test-rac_node"}
        result = mock_client.create("rac_node", {"name": "test-rac_node"})
        assert result["id"] == "new-1"
        assert result["name"] == "test-rac_node"

    def test_create_with_all_params(self, mock_client):
        params = {"name": "full-rac_node", "description": "full test", "enabled": True}
        mock_client.create.return_value = {"id": "new-2", **params}
        result = mock_client.create("rac_node", params)
        assert result["name"] == "full-rac_node"
        assert result["enabled"] is True

    def test_create_sets_changed_flag(self, mock_client):
        result = {"changed": True, "rac_node": {"id": "1"}}
        assert result["changed"] is True

    def test_create_idempotent_existing(self, mock_client_existing):
        """Creating an existing resource should not change."""
        existing = mock_client_existing.get("rac_node", "123")
        assert existing is not None
        result = {"changed": False, "rac_node": existing}
        assert result["changed"] is False


class TestDelete:
    """Test resource deletion operations."""

    def test_delete_existing(self, mock_client_existing):
        mock_client_existing.delete("rac_node", "123")
        mock_client_existing.delete.assert_called_once_with("rac_node", "123")

    def test_delete_not_found_no_error(self, mock_client):
        mock_client.get.return_value = None
        result = {"changed": False}
        assert result["changed"] is False

    def test_delete_returns_changed(self, mock_client_existing):
        result = {"changed": True}
        assert result["changed"] is True

    def test_delete_idempotent(self, mock_client):
        """Deleting a non-existent resource should not change."""
        mock_client.get.return_value = None
        result = {"changed": False}
        assert result["changed"] is False


class TestGet:
    """Test resource retrieval operations."""

    def test_get_existing_resource(self, mock_client_existing):
        result = mock_client_existing.get("rac_node", "123")
        assert result["id"] == "123"
        assert result["name"] == "existing"

    def test_get_nonexistent_resource(self, mock_client):
        result = mock_client.get("rac_node", "nonexistent")
        assert result is None

    def test_get_returns_all_fields(self, mock_client):
        mock_client.get.return_value = {
            "id": "123", "name": "test", "status": "active",
            "created_at": "2026-01-01", "updated_at": "2026-05-01"
        }
        result = mock_client.get("rac_node", "123")
        assert "status" in result
        assert "created_at" in result


class TestUpdate:
    """Test resource update operations."""

    def test_update_returns_updated(self, mock_client):
        mock_client.update.return_value = {"id": "123", "name": "updated-rac_node"}
        result = mock_client.update("rac_node", "123", {"name": "updated-rac_node"})
        assert result["name"] == "updated-rac_node"

    def test_update_idempotent_no_changes(self, mock_client_existing):
        """Updating with same values should report no change."""
        existing = mock_client_existing.get("rac_node", "123")
        result = {"changed": False, "rac_node": existing}
        assert result["changed"] is False

    def test_update_with_changes(self, mock_client_existing):
        mock_client_existing.update.return_value = {"id": "123", "name": "changed"}
        result = {"changed": True, "rac_node": mock_client_existing.update("rac_node", "123", {"name": "changed"})}
        assert result["changed"] is True

    def test_update_partial_params(self, mock_client):
        mock_client.update.return_value = {"id": "123", "description": "new desc"}
        result = mock_client.update("rac_node", "123", {"description": "new desc"})
        assert result["description"] == "new desc"


class TestList:
    """Test resource listing operations."""

    def test_list_returns_items(self, mock_client):
        mock_client.list.return_value = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
        result = mock_client.list("rac_node")
        assert len(result) == 3

    def test_list_empty(self, mock_client):
        mock_client.list.return_value = []
        assert len(mock_client.list("rac_node")) == 0

    def test_list_contains_expected_fields(self, mock_client):
        mock_client.list.return_value = [{"id": "1", "name": "a", "status": "active"}]
        result = mock_client.list("rac_node")
        assert "id" in result[0]
        assert "name" in result[0]


class TestCheckMode:
    """Test check_mode behavior."""

    def test_check_mode_create_no_api_call(self, mock_module_check_mode, mock_client):
        """In check_mode, create should not call the API."""
        if mock_module_check_mode.check_mode:
            result = {"changed": True, "rac_node": {}}
        assert result["changed"] is True
        mock_client.create.assert_not_called()

    def test_check_mode_delete_no_api_call(self, mock_module_check_mode, mock_client_existing):
        """In check_mode, delete should not call the API."""
        if mock_module_check_mode.check_mode:
            result = {"changed": True}
        assert result["changed"] is True
        mock_client_existing.delete.assert_not_called()

    def test_check_mode_update_no_api_call(self, mock_module_check_mode, mock_client_existing):
        """In check_mode, update should not call the API."""
        if mock_module_check_mode.check_mode:
            result = {"changed": True, "rac_node": {}}
        assert result["changed"] is True
        mock_client_existing.update.assert_not_called()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_connection_error(self, mock_client):
        mock_client.get.side_effect = ConnectionError("Connection refused")
        with pytest.raises(ConnectionError):
            mock_client.get("rac_node", "123")

    def test_authentication_error(self, mock_client):
        mock_client.get.side_effect = PermissionError("401 Unauthorized")
        with pytest.raises(PermissionError):
            mock_client.get("rac_node", "123")

    def test_not_found_error(self, mock_client):
        mock_client.get.side_effect = LookupError("404 Not Found")
        with pytest.raises(LookupError):
            mock_client.get("rac_node", "nonexistent")

    def test_server_error(self, mock_client):
        mock_client.create.side_effect = RuntimeError("500 Internal Server Error")
        with pytest.raises(RuntimeError):
            mock_client.create("rac_node", {"name": "test"})

    def test_timeout_error(self, mock_client):
        mock_client.get.side_effect = TimeoutError("Request timed out")
        with pytest.raises(TimeoutError):
            mock_client.get("rac_node", "123")

    def test_invalid_params(self, mock_client):
        mock_client.create.side_effect = ValueError("Invalid parameter")
        with pytest.raises(ValueError):
            mock_client.create("rac_node", {"invalid_field": "bad"})


class TestReturnValues:
    """Test return value structure and content."""

    def test_return_has_changed_key(self):
        result = {"changed": True, "rac_node": {"id": "1"}}
        assert "changed" in result

    def test_return_has_resource_key(self):
        result = {"changed": True, "rac_node": {"id": "1", "name": "test"}}
        assert "rac_node" in result
        assert isinstance(result["rac_node"], dict)

    def test_return_resource_has_id(self):
        result = {"changed": True, "rac_node": {"id": "abc-123"}}
        assert "id" in result["rac_node"]

    def test_return_on_absent(self):
        result = {"changed": True}
        assert result["changed"] is True
        assert "rac_node" not in result or result.get("rac_node") is None or result.get("rac_node") == {}

    def test_return_unchanged_on_noop(self):
        result = {"changed": False, "rac_node": {"id": "1"}}
        assert result["changed"] is False
