# Changelog

## 18.0.1.10

Fix ValueError (singleton: res.users) in model `formio.form` method `_onchange_portal` (which should be reimplemented / migrated).

## 18.0.1.9

Major and important change in access rights of the `formio.form` method `get_form`.
From now this method will not `sudo` by default, to be able to check access rights.
The `get_form` now accepts the `sudo` argument (default `False`) to enfore `sudo` if needed.

Improvements to the portal:
- Improve form access rights for portal user.
- Allow/disallow to cancel a form in the portal, by a setting in the form builder.

## 18.0.1.8

Add URLs (tab) in `formio.form` form view.

## 18.0.1.7

Improve the model (fields) translations with English/en_US (if enabled) reversed translations, in case en_US is not the primary language.

## 18.0.1.6

In the form builder:
- Add configurable Model (fields) translations.\
  Eg useful in select components with the URL Data Source and the getData API.
- Improve info in Translations tab.

## 18.0.1.5

Fixes for public form:
- Fix response for public submission endpoint.
- Fix `_generate_odoo_domain` method for public form.

## 18.0.1.4

Change `formio.form` method `_generate_odoo_domain` to provide the `formio.form` record in args.

## 18.0.1.3

Fix (migration 18) `copy` method in models:
- `formio.builder`
- `ir_actions`
- `ir_attachment`

Since Odoo 18 the `copy` method applies on a multi record set.

## 18.0.1.2

Ensure sufficient formio.js versions (GitHub tags) are downloaded and registered.\
In future versions this will be more configurable.

## 18.0.1.1

Possibility to override the form submit (input) value, by slurping from the input (DOM) element value.\
This is especially useful for external JavaScript (scripts) that modify DOM input elements.

## 18.0.1.0

Initial 18.0 release.
