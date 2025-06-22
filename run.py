from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
import os

# Asegurate de tener esto al final del archivo
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render define PORT como variable de entorno
    app.run(host='0.0.0.0', port=port)
