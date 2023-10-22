class SpeechListener:
    def __init__(self):
        self.message = ""
        self.mode = 0

    def commands(self, text):
        if text == "continue":
            self.mode = 1
        elif text == "replace":
            self.mode = 2
        elif text == "remove":
            self.mode = 3
        elif text == "again":
            self.message = ""
        else:
            print("unknown command.")

    def startListening(self):
        self.mode = 1
        self.message = ""

    def stopListening(self):
        self.mode = 0
        self.message = ""

    def getSpeechMode(self):
        return self.mode
    
    def getText(self):
        return self.message
    
    def setMessage(self, text):
        self.message = text