'''
By Andrew Miller - 10/5/18

This processes an HTML file of a Facebook conversation to prepare the
data for the Facebook text generator.

For now, it only uses HTML data, which can be downloaded in the
settings of any Facebook account. JSON is also available but I had
access to the HTML at the time so that's what I coded it in. If I
ever come back to this project, I'll probably make it JSON 
compatible.

To run:

python conv.py <html file> > <txt file name>   

note: I just made it print the result instead of saving
      to a text file so I just the output to a file when I run it.
 
      Will fix this in the future.
'''
from HTMLParser import HTMLParser
import sys
import re
class FbParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.count = 0
    self.text = "" 
 
  def handle_data(self,data):
    self.count += 1
    if self.count > 1:
      data = analyze_text(data)
      if len(data) > 0:
        if not re.search(r"((\.|\!|\?))$",str(data)[-1]):
          data += "."
        self.text += " " + data + " "

  def getText(self):
    return self.text

def analyze_text(text):
  text = re.sub(r"([0-9]+)\s([a-zA-Z]+)\s([0-9]+)\s([0-9]+):([0-9]+)", "",text)
  text = re.sub(r"\S+\ssent\sa\sphoto","",text,flags=re.IGNORECASE)
  '''
	Sorry about the hard code, I got lazy when I added this part
    	To use with your own Facebook conversation, replace the names the of the
	participants of the conversation.

	This subs out the names from the text data to avoid noise from the
	names appearing so often.  
  ''' 
  text = re.sub("(andy\smiller)|(friend\sname)","",text,flags=re.IGNORECASE)
  return text 

def main():
  for arg in sys.argv[1:]:
    f = open(arg,"r")
    raw = f.read()
    raw = re.sub(r"&\#039;","'",raw)
    parser = FbParser()
    parser.feed(raw)
    text = parser.getText()
    post = re.search(r"\'",text)
    print text    

if __name__ == "__main__":
  main()
