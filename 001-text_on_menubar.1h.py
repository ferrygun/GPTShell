#!/Users/ferry.djaja/anaconda3/bin/python

# <xbar.title>GPT-Shell</xbar.title>
# <xbar.version>1.1</xbar.version>
# <xbar.author>Ferry Djaja</xbar.author>
# <xbar.author.github>https://github.com/ferrygun/GPTShell</xbar.author.github>
# <xbar.desc>GPT-Shell: Your Natural Language-Powered CLI Assistant</xbar.desc>
# <xbar.dependencies>python</xbar.dependencies>
# <xbar.image></xbar.image>

import argparse
import os
import subprocess
import re
import sys
import textwrap
from enum import Enum

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import json
import ast

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain import LLMChain

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-07-01-preview"
os.environ["OPENAI_API_BASE"] = ""
os.environ["OPENAI_API_KEY"] = ""


def get_text_file():
    home = os.path.expanduser("~")
    text_file = os.path.join(home, '.bitbar_text_on_menubar')
    return text_file


def get_file_path():
    return os.path.realpath(__file__)


def get_file_name():
    return os.path.basename(__file__)


def read_and_print():
    print('GPT-Shell')

def get_selected_option():
    while True:
        try:
            with open('/tmp/options.txt', 'r') as f:
                file_content = f.read()

            options = escape_backslashes(file_content)

            with open('/tmp/options_process.txt', 'w') as f:
                f.write(options)

        
            selected_option = subprocess.check_output([
                'osascript',
                '-e',
                #'set options to {"A", "B"}',
                f'set options to {options}',
                '-e',
                'set selected_option to choose from list options with prompt "Please choose an option:" default items {""} without multiple selections allowed and empty selection allowed',
            ], text=True)
            


            return selected_option
        except subprocess.CalledProcessError as er:
            print("Error opening the dialog box. Retrying in x seconds...")
            with open('/tmp/error.txt', 'w') as f:
                f.write(er)
            time.sleep(2)

def escape_backslashes(input_string):
    escaped_string2 = input_string.replace("\n", "\\\\n")

    return escaped_string2


def set_text():
    try:
        ret = subprocess.check_output(
            [
                'osascript',
                '-e',
                r'set input_text to text returned of (display dialog "Please input here:"'
                ' default answer "" with title "Convey your goal in a single sentence")',
            ])
        text = ret.strip().decode("utf-8")
        

        llm = AzureChatOpenAI(
            deployment_name="gpt-4",
            n=3,
            temperature=1
        )

        system_message = "You are an expert at using shell commands in Mac OS. Only provide a single executable line of shell code as output. Never output any text before or after the shell code, as the output will be directly executed in a shell. You're allowed to chain commands like `ls | grep .txt` but make it simple. Reply with 3 suggestions in this format: [\"a\", \"b\", \"c\"]"
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_message)

        human_template="{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])


        def get_suggestions(prompt):
            text=f"Here's what I'm trying to do: {prompt}"

            chain = LLMChain(llm=llm, prompt=chat_prompt)
            results_string = chain.run(text=f"Here's what I'm trying to do: {prompt}")

            return results_string

        options = get_suggestions(text)
        print(options)

        list_as_string = str(options)[1:-1]

        with open('/tmp/options.txt', 'w') as f:
            f.write(options)

        selected_option = get_selected_option();
        with open('/tmp/data.txt', 'w') as f:
            f.write(selected_option)


        terminal_script = f'''\
        tell application "Terminal"
        do script "{selected_option}"
        activate
        end tell
        '''

        # Save the script to a temporary AppleScript file
        with open('/tmp/terminal_script.scpt', 'w') as script_file:
            script_file.write(terminal_script)

        # Run the AppleScript to open Terminal and execute the command
        subprocess.run(['osascript', '/tmp/terminal_script.scpt'])

        # Clean up the temporary AppleScript file
        subprocess.run(['rm', '/tmp/terminal_script.scpt'])
        

    except subprocess.CalledProcessError:
        time.sleep(2)
        

def print_submenu():
    print('---')
    print(('Convey your goal in a single sentence | bash="{}" param1="-s" terminal=false'.format(get_file_path())))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--set_text",
                        action="store_true", help='What you want to do')
    args = parser.parse_args()

    if args.set_text:
        set_text()
        return
    read_and_print()
    print_submenu()
    

if __name__ == '__main__':
    main()
