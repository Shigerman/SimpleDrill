class User:
    """Represents logged-in user and their actions"""

    @staticmethod
    def register(login: str, password: str, invite: str) -> User:
        pass


    @staticmethod
    def login(login: str, password: str) -> User:
        pass
    

    def logout(self):
        pass


    def want_test(self):
        pass


    def submit_test_answer(self, answer: str):
        pass


    def want_drill(self):
        pass


    def select_drill_topic(self, topic: str):
        pass


    def submit_drill_answer(self, answer: str):
        pass


    def give_up_drill(self):
        pass
