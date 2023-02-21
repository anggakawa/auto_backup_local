# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2015 Agile Business Group <http://www.agilebg.com>
# Copyright 2016 Grupo ESOC Ingenieria de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import shutil
import traceback
import json
import tempfile

from contextlib import contextmanager
from datetime import datetime, timedelta
from glob import iglob

import odoo

import odoo.sql_db
import odoo.tools

from odoo import _, api, exceptions, fields, models, tools
from odoo.exceptions import UserError
from odoo.service import db

_logger = logging.getLogger(__name__)

class DbBackup(models.Model):
    _description = "Database Backup"
    _name = "db.backup"
    _inherit = "mail.thread"

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        (
            "days_to_keep_positive",
            "CHECK(days_to_keep >= 0)",
            "I cannot remove backups from the future. Ask Doc for that.",
        ),
    ]

    name = fields.Char(
        compute="_compute_name",
        store=True,
        help="Summary of this backup process",
    )
    folder = fields.Char(
        default=lambda self: self._default_folder(),
        help="Absolute path for storing the backups",
        required=True,
    )
    days_to_keep = fields.Integer(
        required=True,
        default=0,
        help="Backups older than this will be deleted automatically. "
        "Set 0 to disable autodeletion.",
    )
    method = fields.Selection(
        [("local", "Local disk")],
        default="local",
        help="Only local cuz SFTP sucks",
    )
    backup_format = fields.Selection(
        [
            ("zip", "zip (includes filestore)"),
            ("dump", "pg_dump custom format (without filestore)"),
        ],
        default="zip",
        help="Choose the format for this backup.",
    )

    def dump_db_manifest(self, cr):
        pg_version = "%d.%d" % divmod(cr._obj.connection.server_version / 100, 100)
        cr.execute("SELECT name, latest_version FROM ir_module_module WHERE state = 'installed'")
        modules = dict(cr.fetchall())
        manifest = {
            'odoo_dump': '1',
            'db_name': cr.dbname,
            'version': odoo.release.version,
            'version_info': odoo.release.version_info,
            'major_version': odoo.release.major_version,
            'pg_version': pg_version,
            'modules': modules,
        }
        return manifest

    def dump_db(self, db_name, stream, backup_format='zip'):
        """Dump database `db` into file-like object `stream` if stream is None
        return a file object with the dump """

        _logger.info('DUMP DB: %s format %s', db_name, backup_format)

        cmd = ['pg_dump', '--no-owner']
        cmd.append(db_name)

        if backup_format == 'zip':
            with tempfile.TemporaryDirectory() as dump_dir:
                filestore = odoo.tools.config.filestore(db_name)
                if os.path.exists(filestore):
                    shutil.copytree(filestore, os.path.join(dump_dir, 'filestore'))
                with open(os.path.join(dump_dir, 'manifest.json'), 'w') as fh:
                    db = odoo.sql_db.db_connect(db_name)
                    with db.cursor() as cr:
                        json.dump(self.dump_db_manifest(cr), fh, indent=4)
                cmd.insert(-1, '--file=' + os.path.join(dump_dir, 'dump.sql'))
                odoo.tools.exec_pg_command(*cmd)
                if stream:
                    odoo.tools.osutil.zip_dir(dump_dir, stream, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                else:
                    t=tempfile.TemporaryFile()
                    odoo.tools.osutil.zip_dir(dump_dir, t, include_dir=False, fnct_sort=lambda file_name: file_name != 'dump.sql')
                    t.seek(0)
                    return t
        else:
            cmd.insert(-1, '--format=c')
            stdin, stdout = odoo.tools.exec_pg_command_pipe(*cmd)
            if stream:
                shutil.copyfileobj(stdout, stream)
            else:
                return stdout

    @api.model
    def _default_folder(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.join(tools.config["data_dir"], "backups", self.env.cr.dbname)

    @api.depends("folder", "method")
    def _compute_name(self):
        """Get the right summary for this job."""
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder

    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for record in self:
            if record.method == "local" and record.folder.startswith(
                tools.config.filestore(self.env.cr.dbname)
            ):
                raise exceptions.ValidationError(
                    _(
                        "Do not save backups on your filestore, or you will "
                        "backup your backups too!"
                    )
                )

    def action_backup(self):
        """Run selected backups."""
        backup = None
        successful = self.browse()

        # Start with local storage
        for rec in self.filtered(lambda r: r.method == "local"):
            filename = self.filename(datetime.now(), ext=rec.backup_format)
            with rec.backup_log():
                # Directory must exist
                try:
                    os.makedirs(rec.folder)
                except OSError as exc:
                    _logger.exception("Action backup - OSError: %s" % exc)

                with open(os.path.join(rec.folder, filename), "wb") as destiny:
                    # Copy the cached backup
                    if backup:
                        with open(backup) as cached:
                            shutil.copyfileobj(cached, destiny)
                    # Generate new backup
                    else:
                        self.dump_db(
                            self.env.cr.dbname, destiny, backup_format=rec.backup_format
                        )
                        backup = backup or destiny.name
                successful |= rec

        # Remove old files for successful backups
        successful.cleanup()

    @api.model
    def action_backup_all(self):
        """Run all scheduled backups."""
        return self.search([]).action_backup()

    @contextmanager
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.name)
            yield
        except Exception:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                body="<p>%s</p><pre>%s</pre>"
                % (_("Database backup failed."), escaped_tb),
                subtype_id=self.env.ref("auto_backup.mail_message_subtype_failure").id,
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(body=_("Database backup succeeded."))

    def cleanup(self):
        """Clean up old backups."""
        now = datetime.now()
        for rec in self.filtered("days_to_keep"):
            with rec.cleanup_log():
                bu_format = rec.backup_format
                file_extension = bu_format == "zip" and "dump.zip" or bu_format
                oldest = self.filename(
                    now - timedelta(days=rec.days_to_keep), bu_format
                )

                if rec.method == "local":
                    for name in iglob(
                        os.path.join(rec.folder, "*.%s" % file_extension)
                    ):
                        if os.path.basename(name) < oldest:
                            os.unlink(name)

    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info(
                "Starting cleanup process after database backup: %s", self.name
            )
            yield
        except Exception:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(  # pylint: disable=translation-required
                body="<p>%s</p><pre>%s</pre>"
                % (_("Cleanup of old database backups failed."), escaped_tb),
                subtype_id=self.env.ref("auto_backup.failure").id,
            )
        else:
            _logger.info("Cleanup of old database backups succeeded: %s", self.name)

    @staticmethod
    def filename(when, ext="zip"):
        """Generate a file name for a backup.

        :param datetime.datetime when:
            Use this datetime instead of :meth:`datetime.datetime.now`.
        :param str ext: Extension of the file. Default: dump.zip
        """
        return "{:%Y_%m_%d_%H_%M_%S}.{ext}".format(
            when, ext="dump.zip" if ext == "zip" else ext
        )
