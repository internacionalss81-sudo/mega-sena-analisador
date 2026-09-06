[app]
title = Mega Analyzer
package.name = megaanalyzer
package.domain = org.megaanalyzer
source.dir = .
source.include_exts = py,json,png,jpg,kv,atlas

version = 1.0.0
requirements = python3==3.11.8,kivy==2.3.0,urllib3,requests

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.private_storage = True
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1