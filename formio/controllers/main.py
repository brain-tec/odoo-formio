# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

import logging
import traceback

from io import BytesIO
from os.path import dirname

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

from odoo import http, _
from odoo.http import request
from odoo.tools.misc import html_escape

_logger = logging.getLogger(__name__)


class FormioBaseController(http.Controller):

    def _exception_load(self, exception, debug=False):
        message = _('Sorry, something went wrong while loading the form. Please contact us.')
        traceback_exc = traceback.format_exc()
        _logger.error(traceback_exc)
        traceback_exc_html = self._traceback_exc_html(exception, traceback_exc, debug=debug)
        return message, traceback_exc_html

    def _exception_submit(self, exception, submission_data, debug=False):
        message = _('Sorry, something went wrong while processing the form. Please contact us.')
        traceback_exc = traceback.format_exc()
        _logger.error(traceback_exc)
        traceback_exc_html = self._traceback_exc_html(exception, traceback_exc, debug=debug)
        return message, traceback_exc_html

    def _traceback_exc_html(self, exception, traceback_exc, debug=False):
        debug = debug or request.session.debug
        se = http.serialize_exception(exception)
        se['debug'] = traceback_exc
        traceback_html = [html_escape(se['debug'])]
        traceback_html = '<br/>'.join(traceback_html)
        traceback_html = traceback_html.replace('\n', '<br/>')
        traceback_html = traceback_html.replace('\\n', '<br/>')
        traceback_html = traceback_html.replace('\\\n', '<br/>')
        traceback_html = traceback_html.replace('\\\\n', '<br/>')
        return traceback_html

    @http.route(['/web/content/<int:id>/fonts/<string:name>'], type='http', auth="public")
    def send_fonts_file(self, id, name, **kwargs):
        """
        WARNING
        -------
        This route (/fonts/) is a rather iffy assumption which could
        cause troubles.  Of course this could be requested by other
        parts, but not yet in standard Odoo routes.

        ----------------------------------------------------------
        TODO DeprecationWarning, odoo.http.send_file is deprecated
        ----------------------------------------------------------
        But:
        http.Stream.from_path only obtains the addons_path, not
        filestore!

        stream = http.Stream.from_path(fontfile_path)
        return stream.get_response()

        Workaround: (to improve/replace in future?)
        still using Odoo <= v15 approach by using Werkzeug
        implementation
        ----------------------------------------------------------

        :param int id: The ID of the file (attachment) which requests the fonts file.
            File(s) requesting this font file, are CSS files (formio.js library).
        :param str name: The name of the fontfile in request.
        """

        ir_attach = request.env['ir.attachment'].sudo()
        attach = ir_attach.browse(id)
        if not attach.formio_asset_formio_version_id:
            msg = 'Request expects a Forms (formio.js) fonts file (id: %s, name: %s' % (id, name)
            _logger.warning(msg)
            return request.not_found(msg)
        attachment_location = request.env['ir.attachment']._storage()
        if attachment_location == 'file':
            attach_dir = dirname(attach.store_fname)
            fonts_dir = '{attach_dir}/fonts/'.format(attach_dir=attach_dir)
            fontfile_path = request.env['ir.attachment']._full_path(fonts_dir)
            fontfile_path += '/%s' % name
            return send_file(fontfile_path, request.httprequest.environ)
        else:
            # Get the font-file via formio.version.asset;
            # don't search ir.attachment directly, as there are no indexes on formio_asset_formio_version_id
            assets = request.env["formio.version.asset"].search(
                [
                    ("version_id", "=", attach.formio_asset_formio_version_id.id),
                ])
            font_asset = assets.filtered(lambda a: a.attachment_id.name == name)
            if not font_asset:
                msg = f"Font {name} not found"
                _logger.warning(msg)
                return request.not_found(msg)
            return send_file(
                BytesIO(font_asset.attachment_id.raw),
                request.httprequest.environ,
                download_name=name,
            )

    @http.route('/formio/license', type='http', auth='public', csrf=False)
    def license(self, **kwargs):
        domain = [
            ('active', '=', True)
        ]
        licenses = request.env['formio.license'].sudo().search(domain)
        res = {
            'licenses': licenses.mapped('key'),
            'language': request.env.context['lang']
        }
        return request.make_json_response(res)
