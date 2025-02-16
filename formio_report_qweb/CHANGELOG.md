# Changelog

## 18.0.1.1

Add (CSS) `page-break-before` and `page-break-inside` by component (API) properties.\
Configuration goes in the component API tab, in the Properties (Key, Value).

Basically (Key => Value):\
- reportPageBreakBefore => always (Adds to HTML style="page-break-before: always;")
- reportPageBreakInside => avoid (Adds to HTML style="page-break-inside: avoid;")

This (API) implementation supports future changes in the Odoo report engine by using these API property names.

## 18.0.1.0

Initial 18.0 release.
