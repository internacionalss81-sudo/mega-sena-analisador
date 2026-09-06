@echo off
cd /d "%~dp0"
echo Verificando status do repositorio...
git status

echo.
echo Salvando alteracoes locais...
git add .

set /p commit_message="Digite a mensagem do commit: "
if "%commit_message%"=="" set commit_message="Atualizacao automatica do projeto"

git commit -m "%commit_message%"

echo.
echo Sincronizando com o GitHub...
git pull --rebase origin main

echo.
echo Enviando para o GitHub...
git push origin main

echo.
if %errorlevel% equ 0 (
    echo Atualizacao concluida com sucesso! O GitHub Actions iniciara o build.
) else (
    echo Ocorreu um erro ao enviar para o GitHub. Verifique as mensagens acima.
)
pause