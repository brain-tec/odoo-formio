# Changelog

## 18.0.1.1

Fix (migration v18) POST endpoint `/formio/storage/filestore` for public user.\
The endpoint restricts auth on user, but there's no public user in the `request.env` object.

## 18.0.1.0

Initial 18.0 release.
