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
            return jsonify({'answer': self.app.agent_coordinator.process_question(question)})

        @self.app.route('/auto', methods=['POST'])
        def auto():
            return jsonify({'question': self.app.agent_coordinator.create_question()})
            
        @self.app.route('/welcome', methods=['POST'])
        def welcome():
            return jsonify({'welcome': self.app.agent_coordinator.process_question('Hola')})