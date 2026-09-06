[app]

title = Mega Analyzer
package.name = megaanalyzer
package.domain = org.megaanalyzer

source.dir = .
source.include_exts = py,json,png,jpg,kv

version = 1.0.0

requirements = python3,kivy==2.3.1

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b

android.allow_backup = True
android.private_storage = True
android.permissions = INTERNET

p4a.bootstrap = sdl2
android.accept_sdk_license = True


[buildozer]

log_level = 2
warn_on_root = 1