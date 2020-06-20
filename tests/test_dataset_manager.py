"""
This module contains unit tests of cevast.dataset.managers package.
"""

import unittest
from enum import IntEnum
from unittest.mock import patch, PropertyMock
from cevast.dataset.dataset import DatasetType, DatasetInvalidError
from cevast.dataset.manager_factory import DatasetManagerFactory


class DummyDatasetType(IntEnum):
    """Dummy DatasetType ENUM used for Mock."""

    RAPIDOS = 1
    CENSYSOS = 2


class DummyRapidosManager():  # pylint: disable=R0903
    """Dummy DatasetManager used for Mock."""


class DummyCensysosManager():  # pylint: disable=R0903
    """Dummy DatasetManager used for Mock."""


class TestDatasetManagerFactory(unittest.TestCase):
    """Unit test class of DatasetManagerFactory class"""

    @patch('cevast.dataset.manager_factory.DatasetType', DummyDatasetType)
    @patch.object(DatasetManagerFactory, '_DatasetManagerFactory__classes', new_callable=PropertyMock)
    def test_create_manager(self, mocked):
        """Test implementation of DatasetManagerFactory method create_manager."""
        # Test to select correct manager
        mocked.return_value = {"RAPIDOS": DummyRapidosManager}
        assert isinstance(DatasetManagerFactory.create_manager(DummyDatasetType.RAPIDOS), DummyRapidosManager)
        assert isinstance(DatasetManagerFactory.create_manager('RAPIDOS'), DummyRapidosManager)
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, DummyDatasetType.CENSYSOS)
        mocked.return_value = {"CENSYSOS": DummyCensysosManager, "RAPIDOS": DummyRapidosManager}
        assert isinstance(DatasetManagerFactory.create_manager(DummyDatasetType.RAPIDOS), DummyRapidosManager)
        assert isinstance(DatasetManagerFactory.create_manager('RAPIDOS'), DummyRapidosManager)
        assert isinstance(DatasetManagerFactory.create_manager(DummyDatasetType.CENSYSOS), DummyCensysosManager)
        assert isinstance(DatasetManagerFactory.create_manager('CENSYSOS'), DummyCensysosManager)

        # Test without manager
        mocked.return_value = {"RAPIDOS": DummyRapidosManager}
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, DummyDatasetType.CENSYSOS)
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, 'CENSYSOS')

        # Test if not instance or part of Enum
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, DatasetType.RAPID)
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, None)
        mocked.return_value = {"VALID": DummyRapidosManager}
        self.assertRaises(DatasetInvalidError, DatasetManagerFactory.create_manager, "VALID")
