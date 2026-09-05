[app]
title = Mega Analyzer
package.name = megaanalyzer
package.domain = org.megaanalyzer
source.dir = .
source.include_exts = py,json,png,jpg,kv
version = 1.0.0
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.private_storage = True
p4a.bootstrap = sdl2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
