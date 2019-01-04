# Facebook Conversation Generator
A program which generates sentences based on data from Facebook conversations. 

The code needs some cleaning. This was initially a school project that generated sentences from Project Gutenberg text but I decided to 
play around with it for a day and this is what I ended up with. I was pleased with the results but I wasn't planning to ever publish any 
of this so the code is sloppy and there is unfortunately a couple spots that require hardcoding (see code comments). I promise I will fix
this all in the future.

To run:
1. python conv.py <fb HTML data> > <txt file>
2. python talker.py <# sentences> [-c] <txt file from above> 

The '-c' tag allows for custom beginnings to the sentences which are hard coded. 
