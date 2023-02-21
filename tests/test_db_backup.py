# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2015 Alessio Gerace <alesiso.gerace@agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import PropertyMock, patch

from odoo import tools
from odoo.exceptions import UserError
from odoo.tests import common

_logger = logging.getLogger(__name__)


model = "odoo.addons.auto_backup.models.db_backup"
class_name = "%s.DbBackup" % model


class TestDbBackup(common.TransactionCase):
    def setUp(self):
        super(TestDbBackup, self).setUp()
        self.Model = self.env["db.backup"]

    @contextmanager
    def mock_assets(self):
        """It provides mocked core assets"""
        self.path_join_val = "/this/is/a/path"
        with patch("%s.db" % model) as db:
            with patch("%s.os" % model) as os:
                with patch("%s.shutil" % model) as shutil:
                    os.path.join.return_value = self.path_join_val
                    yield {
                        "db": db,
                        "os": os,
                        "shutil": shutil,
                    }

    def test_check_folder(self):
        """It should not allow recursive backups"""
        rec_id = self.new_record("local")
        with self.assertRaises(UserError):
            rec_id.write(
                {
                    "folder": "%s/another/path"
                    % tools.config.filestore(self.env.cr.dbname),
                }
            )

    def test_action_backup_local(self):
        """It should backup local database"""
        rec_id = self.new_record("local")
        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_action_backup_local_cleanup(self):
        """Backup local database and cleanup old databases"""
        rec_id = self.new_record("local")
        old_date = datetime.now() - timedelta(days=3)
        filename = rec_id.filename(old_date)
        with patch("%s.datetime" % model) as mock_date:
            mock_date.now.return_value = old_date
            rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(2, len(generated_backup))

        filename = rec_id.filename(datetime.now())
        rec_id.action_backup()
        generated_backup = [f for f in os.listdir(rec_id.folder) if f >= filename]
        self.assertEqual(1, len(generated_backup))

    def test_action_backup_all_search(self):
        """It should search all records"""
        rec_id = self.new_record()
        with patch("%s.search" % class_name, new_callable=PropertyMock):
            rec_id.action_backup_all()
            rec_id.search.assert_called_once_with([])

    def test_action_backup_all_return(self):
        """It should return result of backup operation"""
        rec_id = self.new_record()
        with patch("%s.search" % class_name, new_callable=PropertyMock):
            res = rec_id.action_backup_all()
            self.assertEqual(rec_id.search().action_backup(), res)

    def test_filename_default(self):
        """It should not error and should return a .dump.zip file str"""
        now = datetime.now()
        res = self.Model.filename(now)
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_zip(self):
        """It should return a dump.zip filenam"""
        now = datetime.now()
        res = self.Model.filename(now, ext="zip")
        self.assertTrue(res.endswith(".dump.zip"))

    def test_filename_dump(self):
        """It should return a dump filenam"""
        now = datetime.now()
        res = self.Model.filename(now, ext="dump")
        self.assertTrue(res.endswith(".dump"))
