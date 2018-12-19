@echo off

echo ## Deleting contents of dist/ and build/ directories...
del /Q /F /S build 
del /Q /F /S dist
del /Q /F /S ..\backend\static
del /Q /F /S ..\backend\static\assets
mkdir ..\backend\static
mkdir ..\backend\static\assets

echo.
echo ## Building Angular app
cd ..\frontend\ctxdoing
call yarn install
call ng build --prod
echo Now at: %cd%
copy dist\ctxdoing ..\..\backend\static\
copy dist\ctxdoing\assets ..\..\backend\static\assets\
cd ..\..\packaging

echo.
echo ## Executing PyInstaller to package into a single EXE...
python -m PyInstaller -F pyinstaller.spec

echo.
echo ## Binary is ready at: %cd%\dist
