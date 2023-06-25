const { Component } = owl;
const { xml } = owl.tags;
const { whenReady } = owl.utils;

// Owl Components
class App extends Component {
    static template = xml`<div id="formio_builder"></div>`;

    willStart() {
        this.loadBuilder();
    }

    loadBuilder() {
        const self = this;
        self.builderId = document.getElementById('builder_id').value;
        self.configUrl = '/formio/builder/' + self.builderId + '/config';
        self.saveUrl = '/formio/builder/' + self.builderId + '/save';
        self.schema = {};
        self.options = {};
        self.params = {};

        $.jsonRpc.request(self.configUrl, 'call', {}).then(function(result) {
            if (!$.isEmptyObject(result)) {
                self.schema = result.schema;
                self.options = result.options;
                self.params = result.params;
                // TODO change this hack, which (maybe) is a silly
                // workaround when Formbuilder object is not ready.
                // Issue reported: https://github.com/novacode-nl/odoo-formio/issues/128
                setTimeout(function() {self.createBuilder();}, 100);
            }
        });
    }

    patchCDN() {
        // CDN class is not exported, so patch it here because
        // ckeditor's URLs are somewhat nonstandard.
        // When using an external CDN, we must also avoid loading the customized
        // version of flatpickr, instead relying on the default version.
	const oldBuildUrl = Formio.cdn.buildUrl.bind(Formio.cdn);
	Formio.cdn.buildUrl = function(cdnUrl, lib, version) {
	    if (lib == 'ckeditor') {
		if (version == '19.0.0') version = '19.0.1'; // Somehow 19.0.0 is missing?!
		return `${cdnUrl}/${lib}5/${version}`;
            } else if (lib == 'flatpickr-formio') {
                return oldBuildUrl(cdnUrl, 'flatpickr', this.libs['flatpickr']);
            } else {
                return oldBuildUrl(cdnUrl, lib, version);
            }
	};
    }

    createBuilder() {
        const self = this;

        this.patchCDN();
	// Ensure when unconfigured, no requests are done
	Formio.cdn.setBaseUrl(self.params['cdn_base_url'] || window.location.href);

        let builder = new Formio.FormBuilder(document.getElementById('formio_builder'), self.schema, self.options);
        let buttons = document.querySelectorAll('.formio_languages button');
        buttons.forEach(function(btn) {
            if (self.options.language === btn.lang) {
                btn.classList.add('language_button_active');
            };
        });

        builder.instance.ready.then(function() {
            if ('language' in self.options) {
                builder.language = self.options['language'];
                // builder.instance.webform.language = self.options['language'];
            }
            window.setLanguage = function(lang, button) {
                builder.instance.webform.language = lang;
                builder.instance.redraw();
                let buttons = document.querySelectorAll('.formio_languages button');
                buttons.forEach(function(btn) {
                    btn.classList.remove('language_button_active');
                });
                button.classList.add('language_button_active');
            };
        });

        builder.instance.on('change', function(res) {
            if (! res.hasOwnProperty('components')) {
                return;
            }
            else if ('readOnly' in self.params && self.params['readOnly'] == true) {
                alert("This Form Builder is readonly (probably locked). Refresh the page and try again.");
                return;
            }
            else {
                console.log('[Forms] Saving Builder...');
                $.jsonRpc.request(self.saveUrl, 'call', {
                    'builder_id': self.builderId,
                    'schema': res
                }).then(function() {
                    console.log('[Forms] Builder sucessfully saved.');
                });
            }
        });
    }
}

// Setup code
function setup() {
    const app = new App();
    app.mount(document.getElementById('formio_builder_app'));
}

whenReady(setup);
