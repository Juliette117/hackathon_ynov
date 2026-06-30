@echo off
title TechCorp AI — Lancement
color 0A

echo.
echo  ████████╗███████╗ ██████╗██╗  ██╗ ██████╗ ██████╗ ██████╗
echo     ██╔══╝██╔════╝██╔════╝██║  ██║██╔════╝██╔═══██╗██╔══██╗
echo     ██║   █████╗  ██║     ███████║██║     ██║   ██║██████╔╝
echo     ██║   ██╔══╝  ██║     ██╔══██║██║     ██║   ██║██╔══██╗
echo     ██║   ███████╗╚██████╗██║  ██║╚██████╗╚██████╔╝██║  ██║
echo     ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝
echo.
echo                   TechCorp AI — Financial Assistant
echo  ================================================================
echo.

:: Vérifier Ollama
echo [1/3] Vérification d'Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERREUR : Ollama n'est pas installé.
    echo  Téléchargez-le sur : https://ollama.com/download
    pause
    exit /b 1
)
echo  OK — Ollama détecté

:: Démarrer Ollama en arrière-plan
echo.
echo [2/3] Démarrage du serveur Ollama...
tasklist | find "ollama" >nul 2>&1
if %errorlevel% neq 0 (
    start /B ollama serve
    timeout /t 3 /nobreak >nul
    echo  OK — Serveur démarré sur http://localhost:11434
) else (
    echo  OK — Ollama déjà en cours d'exécution
)

:: Vérifier si le modèle existe, sinon le télécharger
echo.
echo [3/3] Vérification du modèle phi3.5-financial...
ollama list | find "phi3.5-financial" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Modèle non trouvé. Création en cours...
    ollama pull phi3.5 >nul 2>&1
    ollama create phi3.5-financial -f ollama_server\Modelfile
    echo  OK — Modèle phi3.5-financial créé
) else (
    echo  OK — Modèle phi3.5-financial disponible
)

:: Lancer l'interface web
echo.
echo  ================================================================
echo   Lancement de l'interface web...
echo  ================================================================
echo.
echo   Accès : ouvrez votre navigateur sur l'interface qui s'ouvre
echo   Pour arrêter : fermez cette fenêtre
echo.
start "" "%~dp0web\index.html"

echo  Interface lancée ! Profitez de TechCorp AI.
echo.
pause
