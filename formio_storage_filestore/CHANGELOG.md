# Changelog

## 18.0.1.4

Fix GET endpoint method `storage_filestore_get`.

## 18.0.1.3

Fix (migration v18) `ir.attachment` creation and linking.\
Switch from field `formio_storage_filestore_user_id` to boolean `formio_storage_filestore`, due the public user could not be present.\
This sets the `formio_storage_filestore_user_id` field to `False` (NULL) and could cause attachments (data) loss in the vaccuum cleanup as wel.\
Added migration to link orphanend `ir.attachment` records present in `formio.form` records submission JSON.

## 18.0.1.2

Fix (migration v18) GET endpoint `/formio/storage/filestore`:\
- Migrate the `send_file` method.
- public user access: The endpoint restricts auth on user, but there's no public user in the `request.env` object.

## 18.0.1.1

Fix (migration v18) POST endpoint `/formio/storage/filestore` for public user.\
The endpoint restricts auth on user, but there's no public user in the `request.env` object.

## 18.0.1.0

Initial 18.0 release.
