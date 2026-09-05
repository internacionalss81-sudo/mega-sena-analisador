@echo off
echo Salvando e enviando alteracoes para o GitHub...
git add .
set /p commit_message="Digite a descricao da atualizacao: "
git commit -m "%commit_message%"
git push origin main
echo.
echo Atualizacao concluida! O GitHub Actions iniciara o build do novo APK.
pause