from flask import render_template, request, jsonify

class UIAgent:
    def __init__(self, app):
        self.app = app

    def run(self):
        @self.app.route('/')
        def home():
            return render_template('index.html')

        @self.app.route('/ask', methods=['POST'])
        def ask():
            question = request.json['question']
            image_data = request.json.get('image')
            
            if image_data:
                # Procesar la imagen si está presente
                return jsonify({'answer': self.app.agent_coordinator.process_image_question(question, image_data)})
            else:
                # Procesar pregunta normal si no hay imagen
                return jsonify({'answer': self.app.agent_coordinator.process_question(question)})

        @self.app.route('/auto', methods=['POST'])
        def auto():
            return jsonify({'question': self.app.agent_coordinator.create_question()})
            
        @self.app.route('/welcome', methods=['POST'])
        def welcome():
            return jsonify({'welcome': self.app.agent_coordinator.process_question('Hola')})