## stego.py
# By Adam Good

# Description:
Just a simple steganography script. It currently can hide a message into the pixels of an image.
Will improve later.

# Recent Update:
Added support for simple command line arguments

# Future Updates
* Clean the code
* Make it able to store any stort of payload, not just text
* Update comments so that they're easier to read and understand

# Usage
* Command line arguments
'''
-c <command>        Specify the command you want the script to execute (hide/unhide)
-m <message_file>   Specify the file that contains the message you'd like to hide
-i <image_file>     Specify the image file that you'd like to hide the message in
-o <output_file>    Specify the file to write the output too
'''
* user interface
'''
(h)ide:    Hide a message
(u)nhide:  Unhide a message
(q)uit:    Stops the program
help:      Prints this help message
Example:\n     Command :-$ hide
'''
