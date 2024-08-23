import curses
from curses.textpad import Textbox, rectangle
import pathlib
import textwrap
from ascii_magic import AsciiArt

class KivyDisplayer:
    def __init__(self, ai_client):
        self.path = str(pathlib.Path(__file__).parent.resolve())
        self.sprites = {
            'annoyed': self.path + '\\sprites/kivy_annoyed.jpg',
            'happy': self.path + '\\sprites/kivy_happy.jpg',#, self.path + '\\sprites/kivy_happy(1).jpg'],
            'sad': self.path + '\\sprites/kivy_sad.jpg',
            'angry': self.path + '\\sprites/kivy_angry.jpg',
        }
        self.screen = curses.initscr()
        self.ASCII_CHARS = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", "."]

        try:
            self.loadMainScreen(self.screen)
        except:
            print("The terminal must be in full screen in order to load Kivy in display mode.")
            exit()

        self.ai_client = ai_client


    def loadMainScreen(self, stdscr):
        #uly ulx  lry  lrx        
        rectangle(stdscr, 28, 5, 40, 120) #input  
 
        # editwin.keypad(True)
        # inp = Textbox(editwin)
        #             
       # rectangle(stdscr, 2, 5, 25, 30) # chat log
        rectangle(stdscr, 2, 5, 25, 120) #expression 
        #inp.edit()
        stdscr.refresh()
        #self.waitForUser(inp)
        
    def waitForUser(inp):
        message = inp.gather()
        


    def interpretEmotion(self, message: str):
        """TODO: interpret emotion and convert the specific sprite that conveys that emotion."""
        response = self.ai_client([
            {"role": "system",
             "content": """
                        Considering the given message, interpret its emotion and classify it. There are two, and ONLY TWO, possible answers.
                        I want you to only reply with the emotion the message is conveying and nothing else. do not write explanations. do not write comments.
                        These are the ONLY POSSIBLE answer types, do not write something that's not on the list.
                        neutral
                        happy
                        angry
                        annoyed
                        sad
                        Reply with only the emotion and nothing else.
                        """
             },
             {"role": "user",
              "content": message}
        ])
        return ''.join(chunk.choices[0].delta.content for chunk in response if type(chunk.choices[0].delta.content) == str)

    def display(self, message):
        self.screen.addstr(29, 6, textwrap.fill(message, 115, initial_indent=" ",subsequent_indent="       ", break_long_words=True))
        self.displayEmotion(message)
        self.screen.refresh()
        #self.getUserResponse()

    def displayEmotion(self, message) -> None:
        emotion_to_display = self.interpretEmotion(message)
        path = self.sprites[emotion_to_display]
        #self.screen.addstr(3, 39, self.imageToAscii(path))
        art = AsciiArt.from_image(path)
        art.to_file('temp.txt', columns=22, monochrome=True)
        with open('temp.txt', 'r') as f:
            lines = f.readlines()
            i = 5
            for line in lines:
                self.screen.addstr(3, i, line)
                i += 1

        