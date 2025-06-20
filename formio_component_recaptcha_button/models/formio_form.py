# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo import fields, models


class Form(models.Model):
    _inherit = 'formio.form'

    def formio_component_class_mapping(self):
        """
        This method provides the formiodata.Builder instantiation the
        component_class_mapping keyword argument.
        """
        component_class_mapping = super().formio_component_class_mapping()
        component_class_mapping["odoo_recaptcha_button"] = "button"
        component_class_mapping["odoo_recaptcha"] = "textfield"
        return component_class_mapping
