class MemoryRouter:


    def __init__(self,retriever):

        self.retriever = retriever



    def route(self,text):


        return self.retriever.retrieve(
            text
        )