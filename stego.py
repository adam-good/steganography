"""
*       Name:       stego.py
*       Author:     Adam Good
*       Updated:    01-23-17
*
*       Description:
*           Just a simple steganography script. It currently can hide a
*           message (from a file) into the pixels of an image. Will improve later.
*
*       Recent Update:
*           Added support for simple command line arguments
*
*       TODO:
*           Clean the code
*           Make it able to store any stort of payload, not just text
*           Update comments so that they're easier to read and understand
"""

import sys
import os
import platform
from collections import namedtuple
from PIL import Image

'''
*   Get bits returs the bit string version of msg
*       msg: A string of characters (probably supports bytes but I haven't tried)
*       return: a list of 1's and 0's to represent the bit string
'''
def get_bits(msg):
    # bits will be the list that contains the bit string
    bits = []

    # Get the decimal value of each character (get numerical value of each byte)
    bytes = (ord(byte) for byte in msg)

    # Iterate through all the bytes and iterate through their bits
    for byte in bytes:
        for i in xrange(8):
            # Append the bits to the list of bits.
            # May or may not explain the bit operators
            bits.append((byte >> i) & 1)
    return bits

'''
*   Hides the data from msg in the data in img and returns the data as out
*       img: An opened (but not loaded) image file
*       msg: A list of characters (Probably supports normal bytes but I haven't tested)
*       out:
'''
def hide_msg(img, msg, out):
    # Load the pixels and get the dimensions of the image.
    pixels = img.load()
    rows,cols = img.size

    # Ensure the length of the message is suitable.
    # We quit if we can't store the length in the first column of the image or the total image is too small
    length = len(msg)
    if (length*8 >= 2**cols):
        print ("[X] Message so big we can't even store the length of it correctly...")
        return None
    if (length*8 > int((rows*cols) / 3)):
        print ("[X] Message to big for the image! Sorry!!")
        return None

    # Convert the length to a list of bits that is the size of one collumn.
    # Initialize the list to all 0s to start.
    bits = [0] * rows
    for i in xrange(rows):
        bits[i] = (length >> i) & 1

    # Store the bits of the length in red color of the first column of the image.
    # One entire column should be pleanty of space for this value on most standard images.
    # TODO: find a better way to do this later.
    for x in xrange(rows):
        r,g,b = pixels[x,0]
        if (r%2 != bits[x]):
            r += 1
        pixels[x,0] = (r,g,b)

    # Get the bits of the actual message.
    # Loop through the image storing the bits as we go
    bits = get_bits(msg)
    i = 0   # Index for bits
    for y in xrange(1,rows):
        for x in xrange(cols):
            r,g,b = pixels[x,y]   # Get the values from pixel
            # If we run out of bits we'll get an IndexError when we try to update the value. That's when we know we're done
            # It would probably be better to do this without having to catch the error but this works for now
            # TODO: Better way to do this
            try:
                # Store three bits at a time into r,g,b respectivly
                r += (1 if (r%2 != bits[i]) else 0)
                g += (1 if (g%2 != bits[i+1]) else 0)
                b += (1 if (b%2 != bits[i+2]) else 0)
                # Update the actual pixel with our new values as well as increment our bit counter
                pixels[x,y] = (r,g,b)
                i += 3
            except IndexError:
                # Set the final pixel and save the image
                pixels[x,y] = (r,g,b)
                img.save(out)
                return

'''
*   Read A Message out of the image
*       img: An opened image file
'''
def read_msg(img):
    # Load the pixels and get the dimensions.
    pixels = img.load()
    rows,cols = img.size

    # First we get the length (in bytes) of the message stored in the first column.
    length = 0
    for i in range(rows):
        r,g,b = pixels[i,0]
        if (r%2 == 1):
            length += 2 ** i
    # Convert the length to bits (1 byte = 8 bits)
    length *= 8

    msg = ''    # msg will store the message
    x = 0       # column number
    y = 1       # row number
    i = 0       # bit number
    bits = []   # list of total bits we get from the image

    # For whatever reason a for loop wasn't working here so I created a while loop. TODO fix the for loop.
    # This loop will continue until we have the correct number of bits from the image.
    while (i < length):
        r,g,b = pixels[x,y]

        # Determine which color has the pixel we want based on i%3 and then set the correct value in bit.
        # 0 = red, 1 = green, 2 = blue
        if (i%3 == 0): bit = r%2
        elif (i%3 == 1): bit = g%2
        elif (i%3 == 2): bit = b%2

        # Append our new bit to the list of bits and increment the counter.
        bits.append(bit)
        i += 1
        # If we've gone through 3 bits we need to move to the next pixel in the column.
        if (i%3 == 0 and i != 0):
            x += 1
            # If we've made it through an entire column we need to move to the next row.
            # Also reset x.
            if (x > rows):
                x = 0
                y += 1

    # Loop through our list of bits, convert them to characters, and append them to the message.
    d = 0   # Store the decimal value of each byte.
    i = 0   # The bit index Counter. We use it to know when we have a full byte.
    for _,bit in enumerate(bits):
        # Convert from binary to decimal one bit at a time.
        d += (2**i) if (bit == 1) else 0
        i += 1
        # if we have all 8 bits add the character to the message and reset variables.
        if (i == 8):
            msg += chr(d)
            d = 0
            i = 0
    return msg

'''
*   Just Prints The Help Information
'''
def print_help():
    print("-------------------------------------")
    print("|My Super Duper Steganography Script|")
    print("-------------------------------------")
    print("Usage: \n")
    print('  (h)ide:    Hide a message')
    print('  (u)nhide:  Unhide a message')
    print('  (q)uit:    Stops the program')
    print('  help:      Prints this help message')
    print('  Example:\n     Command :-$ hide\n')


'''
*    Just clears the screen
'''
def clear():
    # Determine the current operating system and clear respectivly
    # If the operating system isn't found (mac for example) just print 30 '\n'
    opsys = platform.system()
    if (opsys == 'Linux'):
        os.system('clear')
    elif (opsys == 'Windows'):
        os.system('cls')
    else:
        print '\n'*30 # Doing this always bugs me but hey, it works!


'''
*   This function handles the user interface
*   It's basically just a control loop.
*   It doesn't execute if the script is executed with command line arguments
'''
def user_interface():
    userInput = ''
    print_help()
    while (userInput != 'quit' and userInput != 'q'):
        userInput = raw_input('Command :-$ ')
        if (userInput == 'hide' or userInput == 'h'):

            # Ask the user for the message file, image file, and output file names
            msgFile = raw_input('  message file: ')
            imgFile = raw_input('  image name: ')
            outputFile = raw_input('  output name: ')

            # Hide the message in the image
            hide(msgFile, imgFile, outputFile)
        elif (userInput == 'unhide' or userInput == 'u'):

            # Get the image and output file names
            imgFile = raw_input('  image name: ')
            outputFile = raw_input('  output name: ')

            # Unhide the image
            unhide(imgFile, outputFile)
        elif (userInput == "help"):
            print_help()
        elif (userInput != 'quit' and userInput != 'q'):
            print('[X] Unknown Command: ' + userInput)
            print_help()


'''
*   Hide the contents of msgName in the pixels of imgName and output ot outName.png
*       msgName: Name of a text file
*       imgName: Name of an image file
*       outName: Name of the file to write new image too
'''
def hide(msgName, imgName, outName):
    # Get the message.
    msgFile = open(msgName)
    msg = msgFile.read()
    msgFile.close()

    # Get the image
    img = Image.open(imgName)

    # Append .png to the output file to make sure our image comes out as a png
    fileType = outName[-4:]
    if (fileType != '.png'):
        outName += '.png'

    # Hide the message, close the image, and have a wonderful day!
    hide_msg(img, msg, outName)
    img.close()
    print '[*] Message hidden in ' + outName

'''
*   Reads a message from imgName and write it out to outName
*       imgName: Name of the image file containing the message
*       outName: Name of the output file
'''
def unhide(imgName, outName):
    # Read from the image
    img = Image.open(imgName)

    # Read the message
    msg = read_msg(img)
    img.close()

    # Write the message to an output file
    output = open(outName, 'w')
    output.write(msg)
    output.close()
    print ('[*] Message Written to ' + outName)


'''
*   Process the commmand line arguments
'''
def processCommandLine():
    # Create a named tuple to help process the arguments
    Vars = namedtuple("Vars", ["command", "msgFile", "imgFile", "outFile"])

    # These variables will be stored into a namedtuple that is return
    command = None
    msgFile = None
    imgFile = None
    outFile = None

    # Try to process the command line arguments.
    # Any errors probably means the arguments are incorrect so we return -1
    # TODO: Try to simplify this process with argparse
    try:
        # Iterate through all of the arguments and update our variables accordingly
        for i,arg in enumerate(sys.argv):
            if (arg == '-c'):
                if (sys.argv[i+1] == 'hide' or sys.argv[i+1] == 'unhide'):
                    command = sys.argv[i+1]
                else:
                    return -1
            elif (arg == '-m'):
                if (os.path.isfile(sys.argv[i+1])):
                    msgFile = sys.argv[i+1]
                else:
                    return -1
            elif (arg == '-i'):
                if (os.path.isfile(sys.argv[i+1])):
                    imgFile = sys.argv[i+1]
                else:
                    return -1
            elif (arg == '-o'):
                outFile = sys.argv[i+1]
    except:
        return -1

    # If they didn't enter an output file supply a default name
    if (outFile == None):
        outFile = "output"

    # Create and return the named tuple of values we got from the arguments
    v = Vars(command, msgFile, imgFile, outFile)
    return v


'''
*   The main function where our program will start
*   Technically not necissary but I think it's good practice
'''
def main():
    argc = len(sys.argv)    # Store the number of arguments

    # If we only have one argument (the program name) start the user interface
    # Otherwise process the arguments and execute accordingly
    if (argc == 1):
        user_interface()
    else:
        args = processCommandLine()
        # if processCommandLine() returns -1 then something went wrong, probably a type
        # if that's the case then stop here, otherwise continue execution
        if (args == -1):
            print("[*] Usage: stego.py -c <hide/unhide> -m <msg> <img>")
            return
        else:
            if (args.command == "hide"):
                hide(args.msgFile, args.imgFile, args.outFile)
            elif (args.command == "unhide"):
                unhide(args.imgFile, args.outFile)

main()
