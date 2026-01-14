🖥️ 1. Desde tu VS Code (Windows)
Estos comandos los ejecutas en la terminal integrada de VS Code (PowerShell o CMD).

A. Desplegar cambios (Rutina Diaria) Usando el script que creamos. Hace commit, push, pull y reinicia el server.

PowerShell

.\deploy.bat
B. Conectarse al Servidor (Entrar a la Matrix) Para entrar a gestionar manualmente.

PowerShell

ssh root@49.13.145.150
☁️ 2. Dentro del Servidor (Vía SSH)
Una vez que estás logueado (root@ubuntu...), usa estos comandos para controlar el backend.

📊 Ver Estado y Logs (Lo más importante)
Ver si el servidor está corriendo: Te dice si está "active (running)" o si murió ("failed").

Bash

systemctl status masterpost
(Presiona q para salir de la vista)

Ver los LOGS en tiempo real: Fundamental si la API tira error 500 y quieres ver el traceback de Python en vivo mientras pruebas la app.

Bash

journalctl -u masterpost -f
(Presiona CTRL + C para detener)

🎮 Controlar el Servicio
Reiniciar el backend: (Útil si cambiaste variables de entorno .env o si se colgó algo).

Bash

systemctl restart masterpost
Detener el backend:

Bash

systemctl stop masterpost
Arrancar el backend: (Si estaba detenido).

Bash

systemctl start masterpost
🛠️ 3. Mantenimiento y Archivos
Ir a la carpeta del proyecto:

Bash

cd /opt/masterpost/backend
Editar variables de entorno (.env): Si necesitas cambiar claves de Supabase o API Keys de IA.

Bash

nano /opt/masterpost/backend/.env
(Guardar: CTRL+O Enter | Salir: CTRL+X)

Verificar tu IP pública:

Bash

curl -4 icanhazip.com
Reiniciar todo el VPS (Opción Nuclear): Si el sistema operativo falla o necesitas aplicar actualizaciones de kernel.

Bash

reboot