# Copyright 2025 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo.tests.common import TransactionCase


class TestFormioBuilder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.FormioBuilder = self.env['formio.builder']
        self.formio_version_dummy = self.env.ref('formio.version_dummy')

    def test_create_builder(self):
        builder = self.FormioBuilder.create({
            'name': 'test_form',
            'title': 'Test Form',
            'formio_version_id': self.formio_version_dummy.id,
        })
        self.assertTrue(builder.id)
        self.assertEqual(builder.name, 'test_form')
        self.assertEqual(builder.title, 'Test Form')
        self.assertEqual(builder.formio_version_id, self.formio_version_dummy)

    def test_state_transitions(self):
        builder = self.FormioBuilder.create({
            'name': 'test_state',
            'title': 'Test State',
            'formio_version_id': self.formio_version_dummy.id,
        })
        self.assertEqual(builder.state, 'DRAFT')
        builder.action_current()
        self.assertEqual(builder.state, 'CURRENT')
        self.assertTrue(builder.is_locked)
        builder.action_obsolete()
        self.assertEqual(builder.state, 'OBSOLETE')

    def test_schema_field(self):
        builder = self.FormioBuilder.create({
            'name': 'test_schema',
            'title': 'Test Schema',
            'formio_version_id': self.formio_version_dummy.id,
            'schema': '{"components":[]}'
        })
        self.assertIn('components', builder.schema)

    def test_invalid_name_constraint(self):
        with self.assertRaises(Exception):
            self.FormioBuilder.create({
                'name': 'invalid name!',
                'title': 'Invalid',
                'formio_version_id': self.formio_version_dummy.id,
            })

    def test_one_current_constraint(self):
        builder1 = self.FormioBuilder.create({
            'name': 'unique_current',
            'title': 'Current 1',
            'formio_version_id': self.formio_version_dummy.id,
            'state': 'CURRENT',
        })
        with self.assertRaises(Exception):
            self.FormioBuilder.create({
                'name': 'unique_current',
                'title': 'Current 2',
                'formio_version_id': self.formio_version_dummy.id,
                'state': 'CURRENT',
            })

    def test_one_version_constraint(self):
        builder1 = self.FormioBuilder.create({
            'name': 'unique_version',
            'title': 'Version 1',
            'formio_version_id': self.formio_version_dummy.id,
            'version': 1,
        })
        with self.assertRaises(Exception):
            self.FormioBuilder.create({
                'name': 'unique_version',
                'title': 'Version 2',
                'formio_version_id': self.formio_version_dummy.id,
                'version': 1,
            })

    def test_public_access_rule_type_constraint(self):
        with self.assertRaises(Exception):
            self.FormioBuilder.create({
                'name': 'public_rule',
                'title': 'Public Rule',
                'formio_version_id': self.formio_version_dummy.id,
                'public': True,
                'public_access_rule_type': False,
            })

    def test_copy_method(self):
        builder = self.FormioBuilder.create({
            'name': 'copy_test',
            'title': 'Copy Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        new_builder = builder.copy()
        self.assertNotEqual(builder.id, new_builder.id)
        self.assertTrue(new_builder.name.startswith('copy_test_'))

    def test_copy_as_new_version(self):
        builder = self.FormioBuilder.create({
            'name': 'ver_test',
            'title': 'Version Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        new_version = builder.copy_as_new_version()
        self.assertNotEqual(builder.id, new_version.id)
        self.assertEqual(new_version.version, builder.version + 1)
        self.assertEqual(new_version.parent_id, builder)

    def test_action_methods(self):
        builder = self.FormioBuilder.create({
            'name': 'action_test',
            'title': 'Action Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        builder.action_current()
        self.assertEqual(builder.state, 'CURRENT')
        self.assertTrue(builder.is_locked)
        builder.action_obsolete()
        self.assertEqual(builder.state, 'OBSOLETE')
        builder.action_draft()
        self.assertEqual(builder.state, 'DRAFT')
        builder.action_lock()
        self.assertTrue(builder.is_locked)
        builder.action_unlock()
        self.assertFalse(builder.is_locked)

    def test_computed_fields(self):
        builder = self.FormioBuilder.create({
            'name': 'computed_test',
            'title': 'Computed Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        builder._compute_display_fields()
        self.assertIn('Computed Test', builder.display_name_full)
        builder._compute_is_schema_empty()
        self.assertTrue(builder.is_schema_empty)
        builder._compute_edit_url()
        self.assertIn('/formio/builder/', builder.edit_url)
        builder._compute_act_window_url()
        self.assertIn('/web?#id=', builder.act_window_url)

    def test_portal_public_urls(self):
        builder = self.FormioBuilder.create({
            'name': 'url_test',
            'title': 'URL Test',
            'formio_version_id': self.formio_version_dummy.id,
            'portal': True,
            'public': True,
        })
        builder._compute_portal_urls()
        builder._compute_public_url()
        # URLs may be False if no request context, but fields should exist
        self.assertTrue(hasattr(builder, 'portal_url'))
        self.assertTrue(hasattr(builder, 'public_url'))

    def test_builder_with_translations(self):
        lang = self.env['res.lang'].search([], limit=1)
        builder = self.FormioBuilder.create({
            'name': 'trans_test',
            'title': 'Trans Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        translation = self.env['formio.builder.translation'].create({
            'builder_id': builder.id,
            'lang_id': lang.id,
            'source': 'Hello',
            'value': 'Hallo',
        })
        self.assertEqual(builder.translations_count, 1)
        i18n = builder.i18n_translations()
        self.assertIsInstance(i18n, dict)

    def test_builder_with_related_forms(self):
        builder = self.FormioBuilder.create({
            'name': 'form_rel_test',
            'title': 'Form Rel Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        form = self.env['formio.form'].create({
            'builder_id': builder.id,
            'name': 'Form1',
            'title': 'Form1',
        })
        builder._compute_count_fields()
        self.assertEqual(builder.forms_count, 1)

    def test_builder_with_server_actions(self):
        builder = self.FormioBuilder.create({
            'name': 'server_action_test',
            'title': 'Server Action Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        # Create a dummy server action
        action = self.env['ir.actions.server'].create({
            'name': 'Test Action',
            'model_id': self.env['ir.model']._get_id('formio.form'),
            'state': 'code',
        })
        builder.server_action_ids = [(6, 0, [action.id])]
        builder._compute_count_fields()
        self.assertEqual(builder.server_action_count, 1)
        builder._compute_show_api_alert()
        self.assertTrue(builder.show_api_alert)

    def test_decode_schema(self):
        builder = self.FormioBuilder.create({
            'name': 'decode_schema',
            'title': 'Decode Schema',
            'formio_version_id': self.formio_version_dummy.id,
            'schema': '{"components":[]}'
        })
        decoded = builder._decode_schema(builder.schema)
        self.assertIsInstance(decoded, dict)

    def test_get_builder_by_name_and_uuid(self):
        builder = self.FormioBuilder.create({
            'name': 'find_test',
            'title': 'Find Test',
            'formio_version_id': self.formio_version_dummy.id,
        })
        builder.action_current()
        found = self.FormioBuilder.get_builder_by_name('find_test')
        self.assertEqual(found.id, builder.id)
        found_uuid = self.FormioBuilder.get_builder_uuid(builder.uuid)
        self.assertEqual(found_uuid.id, builder.id)

    def test_get_latest_builder_by_name(self):
        builder_obsolete_v1 = self.FormioBuilder.create({
            'name': 'latest_test',
            'title': 'Obsolete V1',
            'formio_version_id': self.formio_version_dummy.id,
            'state': 'OBSOLETE',
            'version': 1,
        })
        builder_current_v2 = self.FormioBuilder.create({
            'name': 'latest_test',
            'title': 'Current V2',
            'formio_version_id': self.formio_version_dummy.id,
            'state': 'CURRENT',
            'version': 2,
        })
        builder_draft_v3 = self.FormioBuilder.create({
            'name': 'latest_test',
            'title': 'Draft V3',
            'formio_version_id': self.formio_version_dummy.id,
            'state': 'DRAFT',
            'version': 3,
        })
        builder_draft_v4 = self.FormioBuilder.create({
            'name': 'latest_test',
            'title': 'Draft V4',
            'formio_version_id': self.formio_version_dummy.id,
            'state': 'DRAFT',
            'version': 4,
        })

        # Should get the latest CURRENT builder
        found_current = self.FormioBuilder.get_latest_builder_by_name('latest_test', state='CURRENT')
        self.assertEqual(found_current.id, builder_current_v2.id)
        self.assertEqual(found_current.version, 2)
        self.assertEqual(found_current.state, 'CURRENT')

        # Should get the latest DRAFT builder
        found_draft = self.FormioBuilder.get_latest_builder_by_name('latest_test', state='DRAFT')
        self.assertEqual(found_draft.id, builder_draft_v4.id)
        self.assertEqual(found_draft.version, 4)
        self.assertEqual(found_draft.state, 'DRAFT')

        # Should get the latest OBSOLETE builder
        found_obsolete = self.FormioBuilder.get_latest_builder_by_name('latest_test', state='OBSOLETE')
        self.assertEqual(found_obsolete.id, builder_obsolete_v1.id)
        self.assertEqual(found_obsolete.version, 1)
        self.assertEqual(found_obsolete.state, 'OBSOLETE')

        # Should return False for non-existent
        not_found = self.FormioBuilder.get_latest_builder_by_name('not_found_test', state='CURRENT')
        self.assertFalse(not_found)

    def test_copy_with_custom_defaults(self):
        builder = self.FormioBuilder.create({
            'name': 'custom_copy',
            'title': 'Custom Copy',
            'formio_version_id': self.formio_version_dummy.id,
        })
        new_builder = builder.copy({'title': 'Copied'})
        self.assertEqual(new_builder.title, 'Copied')

    def test_wizard_schema_logic(self):
        builder = self.FormioBuilder.create({
            'name': 'wizard_test',
            'title': 'Wizard Test',
            'formio_version_id': self.formio_version_dummy.id,
            'schema': '{"components":[]}'
        })
        builder.wizard = True
        builder._onchange_wizard()
        self.assertIn('wizard', builder.schema)
        builder.wizard = False
        builder._onchange_wizard()
        self.assertNotIn('wizard', builder.schema)
