# Changelog

## 17.0.1.0.2

Fix "Print Reports" wizard BytesIO error.\
In `formio.form.report.qweb.wizard` method `_generate_qweb_report` convert the BytesIO object to bytes.

Fix `ir.actions.report` instance method `_render` call by providing the report_name argument.

Fix (migration 17) `formio.form.report.qweb.wizard` view.

Fix (migration 17) in `formio.view_formio_builder_form` view:\
In tree view for field `report_print_wizard_ids` migrate fields argument from `invisible` to `column_invisible`.

## 17.0.1.0.1

Improve the `selectboxes_component` QWeb template when the Data Source Type is URL.

## 17.0.1.0

Initial release.
