```ini
[app]

# Nome do aplicativo
title = Mega Analyzer

# Nome interno do aplicativo
package.name = megaanalyzer

# Identificação do aplicativo
package.domain = org.megaanalyzer

# Pasta onde está o código
source.dir = .

# Arquivos que serão incluídos
source.include_exts = py,json,png,jpg,kv

# Versão
version = 1.0.0

# Dependências
requirements = python3,kivy==2.3.0

# Tela vertical
orientation = portrait

# Não usar tela cheia
fullscreen = 0

# Android
android.api = 33
android.minapi = 21

# Arquiteturas
android.archs = arm64-v8a

# Permitir backup
android.allow_backup = True

# Armazenamento privado
android.private_storage = True

# Bootstrap
p4a.bootstrap = sdl2

# Aceitar licença do Android
android.accept_sdk_license = True


[buildozer]

# Nível de log
log_level = 2

# Avisar se executar como root
warn_on_root = 1
```
