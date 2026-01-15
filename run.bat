@echo off
chcp 65001 > nul
echo ========================================
echo   개발시스템 관리 포털 실행
echo ========================================
echo.

cd /d "%~dp0"

echo Streamlit 앱을 시작합니다...
echo 브라우저에서 http://localhost:8501 로 접속하세요.
echo.
echo 종료하려면 이 창에서 Ctrl+C 를 누르세요.
echo ========================================
echo.

python -m streamlit run app.py --server.port 8501

pause
