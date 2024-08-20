class DialogAgent:
    def __init__(self):
        self.dialog = []

    def update_dialog(self, message, is_assistant=False):
        role = "assistant" if is_assistant else "user"
        self.dialog.append({"role": role, "content": message})
        return self.dialog

    def delete_last_dialog(self):
        self.dialog.pop()
        return self.dialog

    def clear_dialog(self):
        self.dialog.clear()