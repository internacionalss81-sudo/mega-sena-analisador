[app]
title = Mega Analyzer
package.name = megaanalyzer
package.domain = org.megaanalyzersource.include_exts = py,png,jpg,kv,atlas,json
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0.0
requirements = python3,kivy,urllib3,requests
orientation = portrait
android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7aandroid.allow_backup = True
android.private_storage = True
p4a.bootstrap = sdl2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
