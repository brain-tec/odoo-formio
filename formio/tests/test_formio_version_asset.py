# Copyright 2025 Nova Code (https://www.novacode.nl)
# See LICENSE file for full licensing details.

from odoo.tests.common import TransactionCase

class TestFormioVersionAsset(TransactionCase):

    def setUp(self):
        super().setUp()
        self.FormioVersion = self.env['formio.version']
        self.FormioVersionAsset = self.env['formio.version.asset']
        self.version = self.FormioVersion.create({
            'name': 'Test',
        })
        self.attachment = self.env['ir.attachment'].create({
            'name': 'Test Attachment',
            'type': 'binary',
            'datas': 'dGVzdA==',  # base64 for 'test'
        })
        self.asset_css = self.FormioVersionAsset.create({
            'version_id': self.version.id,
            'type': 'css',
            'attachment_id': self.attachment.id,
        })
        self.asset_js = self.FormioVersionAsset.create({
            'version_id': self.version.id,
            'type': 'js',
            'attachment_id': self.attachment.id,
        })
        self.asset_license = self.FormioVersionAsset.create({
            'version_id': self.version.id,
            'type': 'license',
            'attachment_id': self.attachment.id,
        })

    def test_version_assets(self):
        self.assertIn(self.asset_css, self.version.assets)
        self.assertEqual(self.asset_css.type, 'css')
        self.assertIn(self.asset_js, self.version.assets)
        self.assertEqual(self.asset_js.type, 'js')
        # license assets are excluded from the main assets field
        self.assertNotIn(self.asset_license, self.version.assets)
        self.assertEqual(self.asset_license.type, 'license')

    def test_create_asset(self):
        asset = self.FormioVersionAsset.create({
            'version_id': self.version.id,
            'type': 'css',
            'attachment_id': self.attachment.id,
        })
        self.assertTrue(asset.id)
        self.assertEqual(asset.version_id, self.version)
        self.assertEqual(asset.type, 'css')

    def test_asset_relations(self):
        self.assertIn(self.asset_css, self.version.css_assets)
        self.assertIn(self.asset_js, self.version.js_assets)
        self.assertIn(self.asset_license, self.version.license_assets)

    def test_unlink_asset(self):
        asset_id = self.asset_css.id
        self.asset_css.unlink()
        self.assertFalse(self.FormioVersionAsset.browse(asset_id).exists())

    def test_update_type_css_js(self):
        self.assertIn(self.asset_css, self.version.assets)
        self.asset_css.write({'type': 'js'})
        self.assertEqual(self.asset_css.type, 'js')
        self.assertIn(self.asset_css, self.version.assets)

    def test_update_type_license(self):
        self.assertIn(self.asset_js, self.version.js_assets)
        self.asset_js.write({'type': 'license'})
        self.assertIn(self.asset_js, self.version.license_assets)
        self.assertNotIn(self.asset_js, self.version.js_assets)

    def test_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "Wrong value for formio.version.asset.type"):
            self.FormioVersionAsset.create({'version_id': self.version.id, 'type': 'invalid', 'attachment_id': self.attachment.id})

    def test_cascade_delete_on_version(self):
        self.version.unlink()
        self.assertFalse(self.FormioVersionAsset.browse(self.asset_css.id).exists())
        self.assertFalse(self.FormioVersionAsset.browse(self.asset_js.id).exists())
        self.assertFalse(self.FormioVersionAsset.browse(self.asset_license.id).exists())

    def test_compute_url(self):
        url_attachment = f'/web/content/{self.attachment.id}/{self.attachment.name}'

        self.assertTrue(isinstance(self.asset_css.url, str))
        self.assertIn(url_attachment, self.asset_js.url)

        self.assertTrue(isinstance(self.asset_js.url, str))
        self.assertIn(url_attachment, self.asset_css.url)

        self.assertTrue(isinstance(self.asset_license.url, str))
        self.assertIn(url_attachment, self.asset_license.url)
