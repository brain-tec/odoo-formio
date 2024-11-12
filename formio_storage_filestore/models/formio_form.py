# Copyright Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo import models


class Form(models.Model):
    _inherit = 'formio.form'

    def after_submit(self):
        res = super().after_submit()
        for rec in self:
            if rec.submission_data:
                rec._process_storage_filestore_ir_attachments()
        return res

    def after_save_draft(self):
        res = super().after_save_draft()
        for rec in self:
            if rec.submission_data:
                rec._process_storage_filestore_ir_attachments()
        return res

    def unlink(self):
        """
        Workaround the ir.attachment its unlink implementation of this module.
        Which blocks deletion of attachment still linked to a user upload
        """
        domain = [
            ('res_model', '=', 'formio.form'),
            ('res_id', 'in', self.ids)
        ]
        attachments = self.env['ir.attachment'].search(domain)
        attachments.write({'formio_storage_filestore_user_id': False})
        return super(Form, self).unlink()

    def _process_storage_filestore_ir_attachments(self):
        attach_names = []
        for key, component in self._formio.input_components.items():
            if component.type == 'datagrid':
                for row in component.rows:
                    for key, component_in_row in row.input_components.items():
                        attach_names += self._get_component_file_names(component_in_row)
            else:
                attach_names += self._get_component_file_names(component)
        # update ir.attachment (link with formio.form)
        import logging
        _logger = logging.getLogger(__name__)
        _logger.critical(attach_names)
        if attach_names:
            domain = [
                ('name', 'in', attach_names),
                ('formio_storage_filestore_user_id', '!=', False)
            ]
            attachments = self.env['ir.attachment'].sudo().search(domain)
            for attach in attachments:
                vals = {
                    'res_model': 'formio.form',
                    'res_id': self.id,
                }
                attach.write(vals)
        # delete ir.attachment (deleted files)
        domain = [
            ('res_model', '=', 'formio.form'),
            ('res_id', '=', self.id),
            ('formio_storage_filestore_user_id', '!=', False)
        ]
        if attach_names:
            domain.append(('name', 'not in', attach_names))
        _logger.critical(domain)
        self.env['ir.attachment'].sudo().search(domain).with_context(
            formio_storage_filestore_force_unlink_attachment=True
        ).unlink()

    def _get_component_file_names(self, component_obj):
        names = []
        if (
            hasattr(component_obj, 'storage')
            and component_obj.storage == 'url'
            and '/formio/storage/filestore' in component_obj.url
            and component_obj.value
        ):
            for val in component_obj.value:
                names.append(val['name'])
        return names
