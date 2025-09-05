# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class BuilderTranslationModel(models.Model):
    _name = 'formio.builder.translation.model'
    _description = 'formio.builder Translation Models'
    _order = 'builder_name ASC, builder_version DESC, lang_name ASC, model_name ASC'

    builder_id = fields.Many2one(
        'formio.builder', string='Form Builder', required=True, ondelete='cascade')
    lang_id = fields.Many2one('res.lang', string='Language', required=True)
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        ondelete='cascade',
        help="Model for which the translations should be loaded."
    )
    model_name = fields.Char(related='model_id.model', string='Model Name', readonly=True, store=True)

    # related fields
    builder_name = fields.Char(related='builder_id.name', string='Builder Name', store=True)
    builder_version = fields.Integer(related='builder_id.version', string='Builder Version', store=True)
    lang_name = fields.Char(related='lang_id.name', string='Language Name', store=True)

    @api.depends('builder_id', 'lang_id', 'model_id')
    def _compute_display_name(self):
        for r in self:
            r.display_name = _('%(lang)s: %(model)s', lang=r.lang_id.name, model=r.model_id.name)

    @api.constrains('builder_id', 'lang_id', 'model_id')
    def _constraint_unique(self):
        errors = []
        for rec in self:
            res = self.search([
                ("builder_id", "=", rec.builder_id.id),
                ("lang_id", "=", rec.lang_id.id),
                ("model_id", "=", rec.model_id.id)
            ])
            if len(res) > 1:
                errors.append(
                    _("- Form Builder Name: {name}\n- Model: {model}\n").format(
                        name=rec.builder_id.name, model=rec.model_name
                    )
                )
        if errors:
            msg = _('Form Builder Translation Models must be unique.\n\n%s') % '\n\n'.join(errors)
            raise ValidationError(msg)
