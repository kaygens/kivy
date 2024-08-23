from groq import Groq
import os
from .prompts import get_commandline_prompt, check_command_safety_prompt, kivy_personality, interpret_intention
import logging
import subprocess
import time
from ..front.welcome import welcome
import sys
import time
from ..front.kivyDisplayer import KivyDisplayer
from blessed import Terminal


logging.basicConfig(
    filename='Kivy',
    level=logging.INFO
)

class Kivy:
    def __init__(self, args):
        self.prompts = {
            'file_management': get_commandline_prompt,
            'check_safety': check_command_safety_prompt,
            'kivy_personality': kivy_personality,
            'interpret_intention': interpret_intention,
        }

        self.styles = Terminal()

        self.context = [{
            "role": "system",
            "content": self.prompts['kivy_personality']
        }]

        self.load_args(args)
        print('[+] fetching env variables...' if self.args.verbose else '')


        self.load_env()
        print('[+] loading kivy model' if self.args.verbose else '')
        self.load_model()
        if self.args.display_image:
            self.displayer = KivyDisplayer(self.generate)
            return
        output = welcome.replace('https://github.com/kaygens', self.styles.link('https://github.com/kaygens', '@kaygens'))
        self.talk(output)

    def load_env(self) -> None:
        try:
            self.key = os.environ.get("GROQ_API_KEY")
        except:
            print('no API key found on environment.')
            exit()
        

    def generate(self, messages=[]): 
        """by default uses self.context, unless messages is specificed"""
        return self.client.chat.completions.create(
            messages=self.context if not messages else messages,
            temperature = 1.3,
            max_tokens = 1024,
            model="llama3-8b-8192",
            top_p = 1,
            stream=True,
            stop=None)
        
    def load_args(self, args):
        self.args = args

    def load_model(self): #probably using groq, but should look for a better alternative
        key = self.load_env()
        try:
            self.client = Groq(
                api_key=key
            )   
        except Exception as e:
            print("[-] Couldn't load Groq model. Forgot to set the api key?")
            exit()

    def getResponse(self, intention: str, inp="Hey! can you introduce yourself to me?") -> str:
        """Generates the final response to the user, """
        self.context.extend([{
            "role": "system",
            "content": self.prompts[intention]
        }, {
            "role": "user",
            "content": inp
        }]
        )
        response = self.generate()
        answer = ''.join(chunk.choices[0].delta.content for chunk in response if type(chunk.choices[0].delta.content) == str)
        self.context.append({
            "role": "assistant",
            "content": answer 
        })
        if intention == 'file_management':
            self.runCommands(answer.strip('][').split(', '))   #<- transform list-like string into actual list
            return ''
        return answer

    def areCommandsSafe(self, cmds: list) -> tuple:
        check_safety: str = self.prompts['check_safety']
        response = self.generate(messages=[
            {
                "role": "system",
                "content": check_safety
            },
            {
                "role": "user",
                "content": ''.join(cmd for cmd in cmds)
            }])
        safety_level, *reason = ''.join(chunk.choices[0].delta.content for chunk in response if type(chunk.choices[0].delta.content) == str).split()
        
        reason = ''.join(word + ' ' for word in reason)

        return (safety_level, reason)

    def interpretIntention(self, message: str):
        interpret_intention = self.prompts['interpret_intention']
        response = self.generate(messages=[{ 
            "role": "system",
            "content": interpret_intention
            },
            {
                "role": "user",
                "content": message
            }],
)
        return ''.join(chunk.choices[0].delta.content for chunk in response if type(chunk.choices[0].delta.content) == str)


    def runCommands(self, commands: list):
        """implements running the commands as subprocesses"""
        safety_level, reason = self.areCommandsSafe(commands)
        if safety_level == 'dangerous':
            self.talk("[!] This command might be dangerous. Run anyway? " \
                  f"Commands: {''.join(command + '\n' for command in commands)}" \
                    f"\nReason: {reason}")
            confirmation = input('(Y/N): ')
            while confirmation == '':
                confirmation = input('(Y/N): ')
            if confirmation not in ['Y', 'y', '']:
                os.system('cls')
                self.start()     #   <- start from scratch.
        try:
            for command in commands:
                command = command.replace('"', '')
                subprocess.run(f'powershell -command "{command}"' , shell=True)
                time.sleep(0.1)
        except Exception as e:
            logging.log(msg=f'[-] {e} ', level=1)


    def start(self):
        self.talk(self.getResponse('kivy_personality'))
        while True:
            inp = input('\n> ')
            intention = self.interpretIntention(inp)
            print('intention: ', intention)
            self.talk(self.getResponse(intention = intention, inp=inp))


    def talk(self, message):
        """TODO: implement talking with some TTS, probably using whisper to convert to audio and then print to terminal in real time."""
        if self.args.display_image:
            self.displayer.display(message = message)
        else:
            print(message)
            
