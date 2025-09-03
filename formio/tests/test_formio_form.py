# Copyright 2025 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo.exceptions import UserError
from odoo.tests import freeze_time
from odoo.tests.common import TransactionCase

from ..utils import json_loads


class TestFormioForm(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FormioBuilder = cls.env['formio.builder']
        cls.FormioForm = cls.env['formio.form']

    def setUp(self):
        super().setUp()
        self.formio_version = self.env['formio.version'].create({
            'name': 'Test Version',
            'is_dummy': True,
        })
        self.builder = self.FormioBuilder.create({
            'name': 'form_test',
            'title': 'Form Test',
            'formio_version_id': self.formio_version.id,
            'public': False,
            'portal': True,
        })

    def test_create_form(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'My Form',
        })
        self.assertTrue(form.id)
        self.assertEqual(form.builder_id, self.builder)
        self.assertEqual(form.title, 'My Form')
        self.assertEqual(form.state, 'PENDING')
        self.assertEqual(form.submission_data, False)
        # test _decode_data with empty submission_data (JSON representation)
        form.submission_data = '{}'
        self.assertEqual(form._decode_data(form.submission_data), {})

    def test_state_transitions(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'State Form',
            'submission_data': '{}',
        })
        form.allow_force_update_state = True
        form.action_draft()
        self.assertEqual(form.state, 'DRAFT')
        form.action_complete()
        self.assertEqual(form.state, 'COMPLETE')
        form.action_cancel()
        self.assertEqual(form.state, 'CANCEL')

    def test_submission_data(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Data Form',
            'submission_data': '{"field1": "value1"}'
        })
        decoded = form._decode_data(form.submission_data)
        self.assertIsInstance(decoded, dict)
        self.assertEqual(decoded['field1'], 'value1')

    def test_copy_form(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Copy Form',
        })
        form.allow_copy = True
        form.copy_to_current = True
        with self.assertRaisesRegex(UserError, "no Form Builder available"):
            new_form = form.action_copy()
        self.builder.state = 'CURRENT'
        # with not self.assertRaisesRegex(UserError, "no Form Builder available"):
        #     new_form = form.action_copy()
        new_form = form.action_copy()
        self.assertNotEqual(form.id, new_form.id)
        self.assertEqual(new_form.state, 'PENDING')
        self.assertEqual(new_form.builder_id.name, form.builder_id.name)

    def test_onchange_builder(self):
        form = self.FormioForm.new({
            'builder_id': self.builder.id,
        })
        form._onchange_builder()
        self.assertEqual(form.title, self.builder.title)
        self.assertEqual(form.show_title, self.builder.show_form_title)
        self.assertEqual(form.show_state, self.builder.show_form_state)
        self.assertEqual(form.show_id, self.builder.show_form_id)
        self.assertEqual(form.show_uuid, self.builder.show_form_uuid)
        self.assertEqual(form.show_user_metadata, self.builder.show_form_user_metadata)

    def test_default_get_and_prepare_create_vals(self):
        defaults = self.FormioForm.default_get(['res_id'])
        self.assertFalse(defaults['res_id'])
        vals = {'builder_id': self.builder.id}
        prepared = self.FormioForm._prepare_create_vals(vals.copy())
        self.assertEqual(prepared['show_title'], self.builder.show_form_title)
        self.assertEqual(prepared['res_model_id'], self.builder.res_model_id.id)

    def test_write_submission_data_forbidden_state(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Forbidden Write',
            'state': 'COMPLETE',
        })
        form.allow_force_update_state = False
        with self.assertRaises(Exception):
            form.write({'submission_data': '{"field": "value"}'})

    def test_clear_res_fields(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Clear Fields',
            'res_model_id': self.builder.res_model_id.id,
            'res_id': 123,
            'initial_res_id': 123,
            'res_name': 'Test',
            'res_partner_id': self.env['res.partner'].create({'name': 'Test'}).id,
        })
        form._clear_res_fields()
        self.assertFalse(form.res_model_id)
        self.assertFalse(form.res_id)
        self.assertFalse(form.initial_res_id)
        self.assertFalse(form.res_name)
        self.assertFalse(form.res_partner_id)

    def test_compute_kanban_group_state(self):
        states = ['PENDING', 'DRAFT', 'COMPLETE', 'CANCEL']
        expected = ['A', 'B', 'C', 'D']
        for state, exp in zip(states, expected):
            form = self.FormioForm.create({
                'builder_id': self.builder.id,
                'title': f'Kanban {state}',
                'state': state,
            })
            form._compute_kanban_group_state()
            self.assertEqual(form.kanban_group_state, exp)

    def test_public_access_expiration(self):
        # builder with no public access
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'No Public Access',
        })
        self.assertFalse(form.public_access)

        # form with explicitly public access
        self.builder.write({
            'public': True,
            'public_access_interval_number': 1,
            'public_access_interval_type': 'minutes',
        })
        with freeze_time('2025-09-03 23:00') as frozen_time:
            form = self.FormioForm.create({
                'builder_id': self.builder.id,
                'title': 'Public Access',
            })
            self.assertTrue(form.public_access)

            frozen_time.move_to('2026-09-04 09:00')
            # form2 = self.FormioForm.browse(form.id)  # reload to trigger compute
            form.invalidate_recordset(["public_access"])
            self.assertFalse(form.public_access)

    def test_get_form_access(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Access Test',
        })
        found = self.FormioForm.get_form(form.uuid, 'read', sudo=True)
        self.assertEqual(found.id, form.id)
        # Should return False for wrong uuid
        not_found = self.FormioForm.get_form('nonexistent', 'read', sudo=True)
        self.assertFalse(not_found)

    def test_get_public_form(self):
        self.builder.public = True
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Public Test',
        })
        found = self.FormioForm.get_public_form(form.uuid, public_share=True)
        self.assertEqual(found.id, form.id)
        not_found = self.FormioForm.get_public_form('nonexistent', public_share=True)
        self.assertFalse(not_found)

    def test_get_js_options_and_params(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'JS Options',
        })
        opts = form._get_js_options()
        self.assertIsInstance(opts, dict)
        self.assertIn('i18n', opts)
        params = form._get_js_params()
        self.assertIsInstance(params, dict)
        self.assertIn('cdn_base_url', params)

    def test_i18n_translations(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'i18n Test',
        })
        i18n = form.i18n_translations()
        self.assertIsInstance(i18n, dict)

    def test_onchange_portal(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Portal Test',
            'portal': False,
        })
        res = form._onchange_portal()
        self.assertIsInstance(res, dict)
        form.portal = True
        res2 = form._onchange_portal()
        self.assertIsInstance(res2, dict)

    def test_compute_url_and_act_window_url(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'URL Test',
        })
        form._compute_url()
        self.assertIn('/formio/form/', form.url)
        self.assertIn('/my/formio/form/', form.portal_url)
        form._compute_act_window_url()
        self.assertIn('/web?#id=', form.act_window_url)

    def test_action_copy_to_current(self):
        self.builder.state = 'CURRENT'
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'CopyToCurrent',
        })
        form.allow_copy = True
        form.copy_to_current = True
        result = form.action_copy_to_current()
        self.assertEqual(result['res_model'], 'formio.form')
        self.assertEqual(result['view_mode'], 'form')

    def test_action_open_res_act_window(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Open Res',
            'res_model_id': self.builder.res_model_id.id,
            'res_model': self.builder.res_model_id.model,
            'res_id': 1,
        })
        result = form.action_open_res_act_window()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], form.res_model)
        self.assertEqual(result['res_id'], 1)

    def test_action_send_invitation_mail(self):
        form = self.FormioForm.create({
            'builder_id': self.builder.id,
            'title': 'Invite',
        })
        result = form.action_send_invitation_mail()
        self.assertEqual(result['res_model'], 'mail.compose.message')
        self.assertEqual(result['type'], 'ir.actions.act_window')
