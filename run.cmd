REM SET FLASK_APP=app.py
REM flask run --host=192.168.1.31 --port=3150
@echo off
netsh interface show interface > temp/netsh_interface_show_interface.txt
netsh wlan show interfaces > temp/netsh_wlan_show_interfaces.txt

REM create empty values
REM set host_wifi_name=
REM set host_net_interfaces=

REM for /f "tokens=1-5" %%a in (temp\netsh_interface_show_interface.txt) do (
REM     IF %%d==Wi-Fi set host_net_interfaces=%%b:%%d
REM )

REM for /f "tokens=1-5" %%a in (temp\netsh_wlan_show_interfaces.txt) do (
REM     IF %%a==SSID set host_wifi_name=%%c %%d
REM )
REM echo Wi-Fi status: %host_net_interfaces%
REM echo Wi-Fi Name: %host_wifi_name%

python manage.py runserver localhost:8000 --settings=web.settings.dev_at_home