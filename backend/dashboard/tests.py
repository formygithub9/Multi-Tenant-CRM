
from unittest.mock import patch

from django.test import SimpleTestCase

from dashboard.services import DashboardService


class DashboardServiceTests(SimpleTestCase):
    @patch("dashboard.services.get_current_database", return_value="shared_db")
    @patch.object(DashboardService, "_count_model")
    @patch.object(DashboardService, "_get_model")
    def test_get_summary_returns_all_configured_modules(
        self, mock_get_model, mock_count_model, mock_database
    ):
        mock_get_model.return_value = object()
        mock_count_model.return_value = {
            "total": 5,
            "by_status": {"OPEN": 3, "COMPLETED": 2},
        }

        summary = DashboardService.get_summary(tenant_id=1)

        self.assertEqual(set(summary), set(DashboardService.MODELS))
        self.assertEqual(summary["customers"]["total"], 5)
        self.assertEqual(
            summary["customers"]["by_status"],
            {"OPEN": 3, "COMPLETED": 2},
        )
        self.assertEqual(mock_count_model.call_count, len(DashboardService.MODELS))
        mock_database.assert_called_once_with()
