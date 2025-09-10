# Copyright Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo.tests.common import TransactionCase


class TestFormioVersionTranslation(TransactionCase):

    def setUp(self):
        super().setUp()
        self.FormioVersion = self.env['formio.version']
        self.FormioVersionTranslation = self.env['formio.version.translation']
        self.FormioTranslation = self.env['formio.translation']
        self.FormioTranslationSource = self.env['formio.translation.source']
        self.lang = self.env['res.lang'].search([], limit=1)
        self.version = self.FormioVersion.create({'name': 'vTransTest'})
        self.source = self.FormioTranslationSource.create({'property': 'prop', 'source': 'src'})
        self.base_translation = self.FormioTranslation.create({'lang_id': self.lang.id, 'source_id': self.source.id, 'value': 'val'})

    def test_create_version_translation(self):
        vt = self.FormioVersionTranslation.create({
            'formio_version_id': self.version.id,
            'base_translation_id': self.base_translation.id,
            'lang_id': self.lang.id,
            'source_property': self.source.property,
            'source_text': self.source.source,
            'value': 'translated',
            'sequence': 1,
        })
        self.assertTrue(vt.id)
        self.assertEqual(vt.formio_version_id, self.version)
        self.assertEqual(vt.base_translation_id, self.base_translation)
        self.assertEqual(vt.lang_id, self.lang)
        self.assertEqual(vt.value, 'translated')

    def test_write_version_translation(self):
        vt = self.FormioVersionTranslation.create({
            'formio_version_id': self.version.id,
            'base_translation_id': self.base_translation.id,
            'lang_id': self.lang.id,
            'source_property': self.source.property,
            'source_text': self.source.source,
            'value': 'translated',
            'sequence': 1,
        })
        vt.write({'value': 'updated'})
        self.assertEqual(vt.value, 'updated')

    def test_unlink_version_translation(self):
        vt = self.FormioVersionTranslation.create({
            'formio_version_id': self.version.id,
            'base_translation_id': self.base_translation.id,
            'lang_id': self.lang.id,
            'source_property': self.source.property,
            'source_text': self.source.source,
            'value': 'translated',
            'sequence': 1,
        })
        vt_id = vt.id
        vt.unlink()
        self.assertFalse(self.FormioVersionTranslation.browse(vt_id).exists())

    def test_compute_base_translation_origin(self):
        # Case 1: base_translation_id is set
        vt = self.FormioVersionTranslation.create({
            'formio_version_id': self.version.id,
            'base_translation_id': self.base_translation.id,
            'lang_id': self.lang.id,
            'source_property': self.source.property,
            'source_text': self.source.source,
            'value': 'translated',
            'sequence': 1,
        })
        self.assertTrue(vt.base_translation_origin)

        # Case 2: base_translation_id is not set
        vt2 = self.FormioVersionTranslation.create({
            'formio_version_id': self.version.id,
            'lang_id': self.lang.id,
            'source_property': self.source.property,
            'source_text': self.source.source,
            'value': 'translated',
            'sequence': 2,
        })
        self.assertFalse(vt2.base_translation_origin)
