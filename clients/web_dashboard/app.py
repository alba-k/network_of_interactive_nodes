# clients/web_dashboard/app.py
import sys
import os
from flask import Flask
from config_dashboard import DashboardConfig
from services.gateway_connector import GatewayConnector
from controllers.main_controller import MainController

# Ajuste de path para que encuentre el resto del proyecto si es necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def create_app():
    app = Flask(__name__)
    app.config.from_object(DashboardConfig)
    
    # Inyección de Dependencias
    gateway = GatewayConnector(DashboardConfig.GATEWAY_API_URL)
    controller = MainController(gateway)
    
    app.register_blueprint(controller.blueprint)
    return app

if __name__ == '__main__':
    print(f"📱 Iniciando Dashboard en puerto {DashboardConfig.WEB_PORT}")
    print(f"🔗 Conectando a Nodo Local en {DashboardConfig.GATEWAY_API_URL}")
    app = create_app()
    app.run(host='0.0.0.0', port=DashboardConfig.WEB_PORT, debug=True)