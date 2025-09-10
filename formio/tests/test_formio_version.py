# Copyright 2025 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo.tests.common import TransactionCase

class TestFormioVersion(TransactionCase):

    def setUp(self):
        super().setUp()
        self.FormioVersion = self.env['formio.version']
        self.FormioVersionGithubTag = self.env['formio.version.github.tag']
        self.FormioTranslation = self.env['formio.translation']
        self.FormioVersionTranslation = self.env['formio.version.translation']

    def test_create_version(self):
        version = self.FormioVersion.create({
            'name': 'Test',
            'description': 'Test version',
            'is_dummy': False,
        })
        self.assertTrue(version.id)
        self.assertEqual(version.name, 'Test')
        self.assertTrue(version.active)

    def test_write_version(self):
        version = self.FormioVersion.create({
            'name': 'Test',
            'description': 'Test write',
        })
        version.write({'name': 'Write2'})
        self.assertEqual(version.name, 'Write2')

    def test_unlink_version(self):
        version = self.FormioVersion.create({
            'name': 'Test',
            'description': 'Test',
        })
        version_id = version.id
        version.unlink()
        self.assertFalse(self.FormioVersion.browse(version_id).exists())

    def test_compute_formio_version_github_tag(self):
        version = self.FormioVersion.create({
            'name': 'Version Tag',
        })
        tag = self.FormioVersionGithubTag.create({
            'formio_version_id': version.id,
            'name': 'Tag1',
        })
        version._compute_formio_version_github_tag()
        self.assertEqual(version.formio_version_github_tag_id, tag)

    def test_base_translations(self):
        version = self.FormioVersion.create({'name': 'Test'})
        lang = self.env['res.lang'].search([], limit=1)
        source = self.env['formio.translation.source'].create({'property': 'p', 'source': 's'})
        base_translation = self.env['formio.translation'].create({'lang_id': lang.id, 'source_id': source.id, 'value': 'v'})
        version.action_add_base_translations()
        self.assertIn(base_translation, version.translation_ids.mapped('base_translation_id'))
        version.action_unlink_base_translations()
        self.assertFalse(version.translation_ids.filtered('base_translation_id'))

    def test_update_versions_sequence(self):
        v1 = self.FormioVersion.create({'name': 'A'})
        v2 = self.FormioVersion.create({'name': 'B'})
        self.FormioVersion._update_versions_sequence()
        self.assertTrue(v1.sequence < v2.sequence)

    def test_archive_dummy_version(self):
        dummy = self.FormioVersion.create({'name': 'Dummy', 'is_dummy': True})
        self.FormioVersion._archive_dummy_version()
        self.assertFalse(dummy.active)

    def test_asset_relations(self):
        version = self.FormioVersion.create({'name': 'vAsset'})
        attachment = self.env['ir.attachment'].create({'name': 'test.css', 'type': 'binary', 'datas': 'dGVzdA==', 'res_model': 'formio.version.asset'})
        css = self.env['formio.version.asset'].create({'version_id': version.id, 'type': 'css', 'attachment_id': attachment.id})
        attachment = self.env['ir.attachment'].create({'name': 'test.css', 'type': 'binary', 'datas': 'dGVzdA==', 'res_model': 'formio.version.asset'})
        js = self.env['formio.version.asset'].create({'version_id': version.id, 'type': 'js', 'attachment_id': attachment.id})
        attachment = self.env['ir.attachment'].create({'name': 'test.js', 'type': 'binary', 'datas': 'dGVzdA==', 'res_model': 'formio.version.asset'})
        lic = self.env['formio.version.asset'].create({'version_id': version.id, 'type': 'license', 'attachment_id': attachment.id})
        self.assertIn(css, version.css_assets)
        self.assertIn(js, version.js_assets)
        self.assertIn(lic, version.license_assets)

    # TODO mock external calls
    # def test_action_reset_download_install(self):
    #     version = self.FormioVersion.create({'name': 'vReset'})
    #     tag = self.FormioVersionGithubTag.create({'formio_version_id': version.id, 'name': 'Tag2'})
    #     called = {'reset': False}
    #     def fake_action(): called['reset'] = True
    #     tag.action_reset_installed = fake_action
    #     version.formio_version_github_tag_id = tag
    #     # version.action_reset_download_install()
    #     self.assertTrue(called['reset'])

    def test_asset_unlink_on_version_unlink(self):
        version = self.FormioVersion.create({'name': 'vAssetUnlink'})
        attachment = self.env['ir.attachment'].create({'name': 'test.txt', 'type': 'binary', 'datas': 'dGVzdA==', 'res_model': 'formio.version.asset'})
        asset = self.env['formio.version.asset'].create({'version_id': version.id, 'type': 'css', 'attachment_id': attachment.id})
        asset_id = asset.id
        version.unlink()
        self.assertFalse(self.env['formio.version.asset'].browse(asset_id).exists())
