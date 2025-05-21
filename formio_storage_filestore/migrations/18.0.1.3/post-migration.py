# Copyright Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    domain = [("state", "=", "COMPLETE")]
    forms = env["formio.form"].search(domain)
    for form in forms:
        attach_names = []
        for key, component in form._formio.input_components.items():
            if component.type == 'datagrid':
                for row in component.rows:
                    for key, component_in_row in row.input_components.items():
                        attach_names += form._get_component_file_names(component_in_row)
            else:
                attach_names += form._get_component_file_names(component)
        # update ir.attachment (link with formio.form)
        if attach_names:
            domain = [
                ('name', 'in', attach_names),
                '|',
                ('res_model', '=', False),
                ('res_model', '=', 'formio.form')
            ]
            attachments = env['ir.attachment'].sudo().search(domain)
            for attach in attachments:
                vals = {
                    'res_model': 'formio.form',
                    'res_id': form.id,
                    'formio_storage_filestore': True
                }
                attach.write(vals)
