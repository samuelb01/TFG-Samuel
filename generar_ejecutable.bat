@echo off
echo ====================================================
echo   Generador de Ejecutable - TFG
echo ====================================================
echo.

echo [1/3] Instalando/Actualizando PyInstaller y dependencias...
:: Asegura que las herramientas necesarias estén instaladas
pip install pyinstaller
pip install -r requirements.txt

echo.
echo [2/3] Generando archivo ejecutable unico...
echo Esto puede tardar unos minutos (especialmente por matplotlib y scipy).
echo.

:: PARAMETROS:
:: --onefile: Empaqueta todo en un solo .exe
:: --noconsole: Evita que se abra la ventana negra de comandos al iniciar la app
:: --name: Nombre que tendrá el archivo final
:: --paths "scripts": Indica donde buscar tus modulos (gui, filter, etc.)
:: "scripts/main.py": Es el punto de entrada de tu aplicacion
python -m PyInstaller --noconsole --onefile --name "TFG_SamuelBellon" --paths scripts scripts\main.py

echo.
echo [3/3] Proceso completado con exito.
echo.
echo El ejecutable se encuentra en la carpeta nueva llamada 'dist'.
echo Puedes mover el .exe a donde quieras.
echo.
echo Nota: Puedes borrar las carpetas 'build' y el archivo '.spec' que se han creado.
echo.
pause