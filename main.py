from features.ai.kivy import Kivy
import logging
from argparse import ArgumentParser
logging.basicConfig(
    filename='Kivy',
    level=logging.INFO
)

def main():
    parser = ArgumentParser(
        prog="Kivy",
        description="AI-driven desktop assistance"
    )
    parser.add_argument('-v', '--verbose',
                        action='store_true')
    parser.add_argument('-display', '--display_image',
                        action='store_true')
    args = parser.parse_args()
    kivy = Kivy(args)

    kivy.start()
    logging.log(msg='[+] running kivy...' if args.verbose else '' , level = 0)



if __name__ == '__main__':
    main()
        