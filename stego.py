"""
*       Name:       stego.py
*       Author:     Adam Good
*       Updated:    12-28-16
*
*       Description:
*           Just a simple steganography script. It currently can hide a 
*           message (from a file) into the pixels of an image. Will improve later.
*
*       TODO:
*           Clean the code
*           Make it able to store any stort of payload, not just text
*           Update comments so that they're easier to read and understand
"""

import sys
import os
import platform
from PIL import Image


def get_bits(msg):
    bits = []
    bytes = (ord(byte) for byte in msg) # Get the decimal value of each byte
    for bit in bytes:
        for i in xrange(8):
            # Append the bits to the list of bits.
            bits.append((bit >> i) & 1)
    return bits


def hide_msg(img, msg, out):
    # Load the pixels and get the dimensions of the image.
    pixels = img.load()
    rows,cols = img.size

    # Ensure the length of the message is suitable.
    # We quit if we can't store the length in the first column or the total image is too small
    length = len(msg)
    if (length*8 >= 2**cols):
        print ("[X] Message so big we can't even store the length of it correctly...")
        return None
    if (length*8 > int((rows*cols) / 3)):
        print ("[X] Message to big for the image! Sorry!!")
        return None
    
    # Convert the length to a list of bits that is the size of one collumn.
    # The default bit value is 0.
    bits = [0] * rows
    for i in xrange(rows):
        bits[i] = (length >> i) & 1
    
    # Store the bits in red color of the first column of the image.
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
            try:
                # Store three bits at a time into r,g,b respectivly
                r += (1 if (r%2 != bits[i]) else 0)
                g += (1 if (g%2 != bits[i+1]) else 0)
                b += (1 if (b%2 != bits[i+2]) else 0)
                # Update the actual pixel with our new values as well as increment our bit counter
                pixels[x,y] = (r,g,b)
                i += 3
            # If we run out of bits we'll get an IndexError when we try to update the vale. That's when we know we're done    
            # It would probably be better to do this without having to catch the error but this works for now
            # TODO: Better way to do this
            except IndexError:
                # Set the final pixel and save the image
                pixels[x,y] = (r,g,b)
                img.save(out)
                return


def read_msg(img):
    # Load the pixels and get the dimensions.
    pixels = img.load()
    rows,cols = img.size

    # First we get the length of the message stored in the first column.
    length = 0
    for i in range(rows):
        r,g,b = pixels[i,0]
        if (r%2 == 1):
            length += 2 ** i
    # Multiply the length by 8 because length is in units of bytes but we are working with bits (8 bits = 1 byte).
    length *= 8
    
    msg = ''    # msg will store the message
    x = 0       # column number
    y = 1       # row number
    i = 0       # bit number
    bits = []   # list of total bits we get from the image
    
    # For whatever reason a for loop wasn't working here so I created a while loop. TODO fix the for loop.
    # This will continue until we have the correct number of bits from the image.
    while (i < length):
        r,g,b = pixels[x,y]
        # Determine which color has the pixel we want based on i%3 and then set the correct value in bit.
        if (i%3 == 0): bit = r%2
        elif (i%3 == 1): bit = g%2
        elif (i%3 == 2): bit = b%2
        # Append our new bit to the list of bits and increment the counter.
        bits.append(bit)
        i += 1
        # If we've gone through 3 bits we need to move to the next pixel (x += 1).
        if (i%3 == 0 and i != 0):
            x += 1
            # If we've made it through an entire column we need to move to the next row (y += 1); Also reset x
            if (x > rows):
                x = 0
                y += 1

    # Loop through our list of bits, convert them to characters, and append them to the msg.
    d = 0   # Store the decimal value of each byte.
    b = 0   # The bit index Counter. We use it to know when we have a full byte.
    for i,bit in enumerate(bits):
        # Convert from binary to decimal one bit at a time.
        d += (2**b) if (bit == 1) else 0
        b += 1
        # if we have all 8 bits add the character to the message and reset variables.
        if (b == 8):
            msg += chr(d)
            d = 0
            b = 0
    return msg


def print_help():
    print("-------------------------------------")
    print("|My Super Duper Steganography Script|")
    print("-------------------------------------")
    print("Usage: \n")
    print('  (h)ide:    Hide a message')
    print('  (u)nhide:  Unhide a message')
    print('  (q)uit:    Stops the program')
    print('  help:      Prints this help message')
    print('  Example:\n     Command :-$ hide "message" img.jpg\n')


def clear():
    opsys = platform.system()
    if (opsys == 'Linux'):
        os.system('clear')
    elif (opsys == 'Windows'):
        os.system('cls')
    else:
        print '\n'*30 # Doing this always bugs me but hey, it works!

def main():
    userInput = ''
    print_help()
    while (userInput != 'quit' and userInput != 'q'):
        userInput = raw_input('Command :-$ ')
        if (userInput == 'hide' or userInput == 'h'):
            # Get the message.
            msgFile = open(raw_input('  message file: '))
            msg = msgFile.read()
            msgFile.close()
            # Get the image
            imgName = raw_input('  image name: ')
            img = Image.open(imgName)

            # Get the name for the output. For simplicity the output will always be a png file            
            output = raw_input('  output name: ') + '.png'

            # Hide the message, close the image, and have a wonderful day!
            hide_msg(img, msg, output)
            img.close()
            print '\n[*] Message hidden in ' + output + '\n'
        elif (userInput == 'unhide' or userInput == 'u'):
            # Get the image to read from
            imgName = raw_input('  image name: ')
            img = Image.open(imgName)
            
            # Read and print the message in a nice format
            clear()
            print ('[*] Begin Message:\n')
            print read_msg(img)
            img.close()
            raw_input('[*] End Message')
            clear()
            print_help()
        elif (userInput != 'quit' and userInput != 'q'):
            print('[X] Unknown Command: ' + userInput)
            print_help()

main()
