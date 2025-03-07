import os
from openai import OpenAI
from instances.openAI_secret import API_KEY

class OpenAIWrapper:
    def __init__(self, keep_whole_context : bool, system_message : str):
        self.client = OpenAI(api_key=API_KEY)
        self.keep_whole_context = keep_whole_context
        self.system_message = system_message
        self.messages = [self.__create_system_message(self.system_message)]

    def __create_user_message(self, content):
        return {"role": "user", "content": content}
    
    def __create_system_message(self, content):
        return {"role": "system", "content": content}
    
    def __create_assistant_message(self, content):
        return {"role": "assistant", "content": content}
    
    def __add_message(self, content):
        if (self.keep_whole_context):
            self.messages.append(self.__create_user_message(content))
        else:
            self.messages = [
                self.__create_system_message(self.system_message),
                self.__create_user_message(content) 
            ]

    def __get_response(self):
        full_response = self.client.chat.completions.create(
            model = "gpt-4-1106-preview",
            messages=self.messages,
            temperature=0,
        )

        response_content = full_response.choices[-1].message.content
        self.messages.append(self.__create_assistant_message(response_content))
        return response_content
    
    def upload_query(self, prompt) -> str:
        self.__add_message(prompt)
        response = self.__get_response()
        return response if response is not None else ""