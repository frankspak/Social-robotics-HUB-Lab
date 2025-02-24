# -*- coding: utf-8 -*-


###########################################################
import os, sys, codecs, json
from datetime import datetime
from threading import Thread
from oaichat.oairesponse import OaiResponse

from dotenv import load_dotenv
load_dotenv()

if sys.version_info[0] < 3:
    raise ImportError('OpenAI Chat requires Python 3')

import openai
from openai import OpenAI

class OaiChat:
  def __init__(self,user,prompt=None):
    self.log = None
    self.reset(user,prompt)
    self.client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

  def reset(self,user,prompt=None):
    self.user = user
    self.history = self.loadPrompt(prompt or os.getenv('OPENAI_PROMPTFILE'))
    self.resetRequestLog()

  def resetRequestLog(self):
    # if (self.log): self.log.close()
    # logdir = os.getenv('LOGDIR')
    # if not os.path.isdir(logdir): os.mkdir(logdir)
    # log = 'requests.%s.%s.log'%(self.user,datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    # self.log = open(os.path.join(logdir,log),'a')
    # print('Logging requests to',log)
    pass

  def respond(self, inputText):
    start = datetime.now()
    self.moderation = None
    #moderator = Thread(target=self.getModeration,args=(inputText,))
    #moderator.start()
    guidance = (
        "Provide a response in a maximum of 4-5 complete sentences."
        "to invite further engagement, such as 'Would you like to know more about this topic?' or 'What would you like to know more?'."
        "Answer in the language spoken to you by the user"
    )

    # Combine guidance with user input
    prompt = f"{guidance}\nUser: {inputText}"
    self.history.append({'role':'user','content':prompt})
    #print(self.history)
    response = self.client.chat.completions.create(
      model="chatgpt-4o-latest",
      #response_format={ "type": "json_object" },
      #user=self.user,
      messages=self.history,
      # temperature=0.7,
      # top_p=1,
      # frequency_penalty=1,
      # presence_penalty=0
    )
    #moderator.join()
    #print('Moderation:',self.moderation)
    print(response.choices[0].message.content)
    r = OaiResponse(response.model_dump_json())
    print("its R",response.model_dump_json() , 'r')

    self.history.append({'role':'assistant','content':r.getText()})
    print('Request delay',datetime.now()-start)
    print(r , 'its r 2')
    return r

  def loadPrompt(self,promptFile):
    promptFile = promptFile or 'openai.prompt'
    promptPath = promptFile if os.path.isfile(promptFile) else os.path.join(os.path.dirname(__file__),promptFile)
    prompt = [] # [{"role": "system", "content": "You are a helpful robot designed to output JSON."}]
    if not os.path.isfile(promptPath):
      print('WARNING: Unable to locate OpenAI prompt file',promptFile)
    else:
      with codecs.open(promptPath,encoding='utf-8') as f:
        prompt.append({'role':'system','content':f.read()})
    return prompt
    
if __name__ == '__main__':
  chat = OaiChat(user='OaiChat')

  while True:
    try:
      s = input('> ')
    except KeyboardInterrupt:
      break
    if s:
      print(chat.history)
      print(chat.respond(s).getText())
    else:
        break
  print('Closing GPT Server')