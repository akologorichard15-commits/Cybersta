[app]
title = Cyberstar
package.name = cyberstar
package.domain = com.cyberstar
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt
version = 1.0.0
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0
android.api = 35
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET
android.add_src = .

[buildozer]
log_level = 2
warn_on_root = 1
