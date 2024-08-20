# main.py
from multi_agent_system import MultiAgentSystem

if __name__ == '__main__':
    system = MultiAgentSystem()
    system.initialize()
    system.run()
    system.app.run(port=5001, debug=True)  # Añadimos esta línea para iniciar el servidor Flask