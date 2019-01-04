'''
  By Andrew Miller 
  andrewjamesmiller31@gmail.com
  10/5/2018

  This started as a school project that generates text based on books from 
  Project Gutenberg. After submitting, I decided I wanted to extend it and see
  what it could do with the data from an 8+ year Facebook conversation I have
  with a good friend of mine. It works fairly well, often generating comedic 
  results.

  Through ngram mining, the program randomly generates sentences that are likely
  to occur in the converation based on frequencies.

  The code needs some cleaning and additional comments, sorry. Also, the threading
  wasn't necessary, I was doing some experimenting. I will remove it in the future
  and clean up everything. 
'''
import sys 
import re 
import operator 
import random 
import datetime
import os
import threading

'''
  To use a custom start to the sentences, hard code each start to the array and   use the '-c' flag.  
'''
custStart = ['i','the']

sentences = None
pnc = r"\,|\.|\!|\?|\:|\;|\-|\)|\("
endSent = r"\.|\?|\!"
strt = "_START_"
end = "_END_"
printCount = 1
mutex = threading.Lock()
ng2 = {} 
ng3 = {}
ng4 = {}
ng5 = {}
# makes a list of strings into a valid key for a dictionary
def makeKey(words):
  key = ""
  for w in words:
    key += w + " "
  return key

'''
  this is an ngram function which uses the user input to find all ngrams in the
  text 
  stn is a list of every sentence found in the text
  returns dictionary of ngram frequencies
'''
def ngrams(stn,ngram):
  # the frequency of each ngram is kept in this dictionary, ng
  # ng stores phrases as the keys and the value is another dictionary containing
  # the possible words that can follow and their frequencies
  ng = {}
 
  # for each sentence
  for s in stn:
    i = 0 
    cur = [] # array used as a buffer to keep track of current ngram
    while i < len(s):
      if len(cur) == ngram-1: # if there are enough words to make an ngram
	# Create a key from the array of words, this key is the phrase
	k = makeKey(cur) 
	# add the next word to complete the ngram
	cur.append(s[i])
        # k2 acts as the key for the nested dict, which is a word that follows k 
	k2 = s[i]+" " 
	# If k already exists, either add k2 or add 1 to k2
        if k in ng:
          ng[k][k2] = 1 if k2 not in ng[k] else ng[k][k2] + 1
        # else add k and k2, initializing count to 1
	else:
 	  ng[k] = {k2:1}
	  
	# delete the first element of the buffer to move onto the next ngram
	del cur[0]
        
      else:
	# else add to the array (this is done until there are enough words to 
	# form an ngram)
	cur.append(s[i])
      i += 1 # move on to the next word
  return ng

# generates a regular expression that will search for the part of a phrase that
# is used to determined the preceding words in an ngram
def nMinusOne(ngram):
  words = r"("
  for i in range(0,ngram-1):
    words += "(\S+)\s"
  words += ")$"
  return words


def avoidBadEnd(ch):
  if len(ch) > 3:
    if ". " in ch:
      if ch[". "] < 10:
        del ch[". "]
    if "! " in ch:
      if ch["! "] < 10:
        del ch["! "] 
    if "? " in ch:
      if ch["? "] < 10:
        del ch["? "]
  return ch  


# chooses the next word to use for a sentence
# ch is a dict of a single word for a key and a frequency for a value
def chooseWord(ch,tCount):
  ch = avoidBadEnd(ch)
  random.seed(datetime.datetime.now())
  # sort by word use frequencies (this seems to help average case time when 
  # ngram = 1)
  sCh = sorted(ch.items(),key=operator.itemgetter(1))
 
  # if ngram is one, total weight (based on frequency) is token count
  # else, count is the sum of the values of the dict ch
  tw = sum(ch.values())
  # choose random number in frequency range
  choice = random.randint(1,tw)
  i=0
  # remove the frequency weight of each word until choice < 1
  # whatever i is left on is the chosen word
  while choice > 1:
    i-=1
    choice -= sCh[i][1]
  return sCh[i][0]

# generates a sentence based off of the ngrams
def genSent(cust,ng2,ng3,ng4,ng5,sCount,tCount):
  if cust:
    word = random.choice(custStart)
    curGram = strt + " " + word + " "
    sent = curGram
  else:
    curGram = strt
    fc = list(k for k in ng2.keys() if re.search("^("+curGram+")",k))
    weights = list( sum(ng2[k].values()) for k in fc )
    curGram = chooseWord( dict((i,weights[fc.index(i)]) for i in fc),tCount)  
    sent = curGram
  wordCount = 2 
  while re.search(end,sent) == None:
    if curGram not in ng5 or len(ng5[curGram].values()) < 2:
      if wordCount > 3:
        curGram = re.findall(nMinusOne(4),sent)[0][0]
      if curGram not in ng4 or len(ng4[curGram].values()) < 2:
	if wordCount > 2:
          curGram = re.findall(nMinusOne(3),sent)[0][0]
        if curGram not in ng3 or len(ng3[curGram].values()) < 2:
          curGram = re.findall(nMinusOne(2),sent)[0][0]
          word = chooseWord(ng2[curGram],tCount)
        else:
          word = chooseWord(ng3[curGram],tCount)
      else:
        word = chooseWord(ng4[curGram],tCount)
    else:
      word = chooseWord(ng5[curGram],tCount)
    sent += word
    # remove the first word from sent to get the next key to be used for chosing words
    # again, if ngram is 1 then simply use ""
    if wordCount > 3:
      curGram = re.findall(nMinusOne(4),sent)[0][0]
    else:
      curGram = re.findall(nMinusOne(wordCount),sent)[0][0] 
    wordCount += 1
  
  # remove the start and end tokens from the sentence and return
  sent = re.sub(strt+r"\s","",sent)
  sent = re.sub(end,"",sent)
  sent = sent[:-4] + sent[-3:]
  return sent.capitalize()


# This function finds each token, and then distinguishes the types by tracking 
# the tokens in a dict
def analyzeText(text):
  types = {}
  tokens = re.findall(r"\S+",text)

  for t in tokens:
    if t in types:
      types[t] += 1
    else:
      types[t] = 1
  return types,tokens

# This function adds the start and end tags (defined above) to the beginning/end
# of each sentence
def findSentences(tokens):
  sentences = [] 
  s = [strt] # start tag
  for t in tokens:
    if re.search(endSent,t):
      if len(s) > 1:
        s.append(t)
        s.append(end)
        sentences.append(s)
        s = [strt]
    else:
      s.append(t)
  return sentences
    
# this function prepares the text for tokenization by putting spaces betweeen 
# punctuation
def prepText(text):
  # Mr. Mrs. and Ms. were causing problems so I just removed the periods
  text = re.sub(r"mr\.","mr",text,flags=re.IGNORECASE)
  text = re.sub(r"mrs\.","mrs",text,flags=re.IGNORECASE)
  text = re.sub(r"ms\.","ms",text,flags=re.IGNORECASE) 
  # I also decided to remove quotation.
  text = re.sub(r"\"","",text)
  text = re.sub(r"\s(http\S+)\s","",text) 
  punc = re.findall(pnc,text) # find every punctuation mark from the defined list above
  ptypes = dict((p,1) for p in punc ) # a dict to keep track of each type of punctuation found
  for k in ptypes.keys():
    text = re.sub("\\"+k," "+k+" ",text) # for each punctuation k, replace with " k "
  return text.lower() # return the text in lowercase for more accurate types


def genThread(cust,num,ls,tok):
  sens = []
  global ng2,ng3,ng4,ng5
  for n in range(0,num):
    sens.append( genSent(cust,ng2,ng3,ng4,ng5,ls,tok))
  mutex.acquire()
  try:
    global printCount
    for sen in sens:
      global printCount
      print str(printCount)+". ",sen,"\n"
      printCount += 1
  finally:
    mutex.release()

def main():
  text = ""
  cust = False
  # read in files named as arguments, add each to text after prepping them
  for arg in sys.argv[2:]:
    if re.search(r"\-c",arg):
      cust = True
    else:
      print "\nReading '" + arg +"'" 
      f = open(arg,"r")
      nt = f.read()
      text += prepText(nt)
  
  # count types and tokens 
  types,tokens = analyzeText(text)
  # extract sentences
  s =  findSentences(tokens) 
  # generate ngrams
  global ng2,ng3,ng4,ng5
  ng2 = ngrams(s,2)
  ng3 = ngrams(s,3)
  ng4 = ngrams(s,4)
  ng5 = ngrams(s,5)
  # generate sentences randomly from ngrams
  startT = datetime.datetime.now()
  
  threads = [] 
  for i in range(0,10):
    t = threading.Thread(target=genThread,args=(cust,sentences/10,len(s),tokens,))
    threads.append(t)
    t.start()    
  for t in threads:
    t.join()
  print "Start time:",startT
  print "Finish time:",datetime.datetime.now()
  print len(tokens),"tokens found."
  print len(types),"types found."
  print "The token/type ratio is", float(len(tokens))/float(len(types))

if __name__ == "__main__":
  # check for valid args
  if len(sys.argv) > 2:
    try:
      sentences = int(sys.argv[1])
    except ValueError:
      print "ERROR: Missing ngram or number of sentences"
  else:
    print "ERROR: Not enough arguments."
    sys.exit() 
  main()
