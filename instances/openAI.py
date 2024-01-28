import os
from openai import OpenAI
from openAI_secret import API_KEY

class OpenAIWrapper:
    def __init__(self, system_message : str):
        self.client = OpenAI(api_key=API_KEY)
        self.messages = [
            {
                "role": "system", 
                "content": system_message
            }
        ]

    def __create_user_message(self, content):
        return {"role": "user", "content": content}
    
    def __create_system_message(self, content):
        return {"role": "system", "content": content}
    
    def __create_assistant_message(self, content):
        return {"role": "assistant", "content": content}
    
    def __add_message(self, content):
        self.messages.append(self.__create_user_message(content))

    def __get_response(self):
        full_response = self.client.chat.completions.create(
            model = "gpt-3.5-turbo-1106",
            messages=self.messages
        )

        response_content = full_response.choices[-1].message.content
        self.messages.append(self.__create_assistant_message(response_content))
        return response_content
    
    def upload_query(self, prompt) -> str:
        self.__add_message(prompt)
        response = self.__get_response()
        return response if response is not None else ""