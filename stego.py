"""
*       Name:       stego.py
*       Author:     Adam Good
*       Updated:    03-04-17
*
*       Description:
*           Just a simple steganography script. It can hide files in an image
*
*       Recent Update:
*           Pretty much rewrote most of it with better functionality and bug fixes
*           It can now hide any binary data (AKA any file type)
*
*       TODO:
*           Clean the code
*           Update comments so that they're easier to read and understand
"""

import sys
import getopt
from PIL import Image

'''
*   Reads the binary data from a file
*       filename:   The name of the file to open and read from
*       return:     list of bytes read from the file
'''
def read_file(filename):
    f = open(filename, "rb")
    try:
        byteStr = f.read()
    finally:
        f.close()

    data = []
    for char in byteStr:
        data.append(ord(char))
    return data

'''
*   Write binary data to a file
*       data:       List of binary data
*       filename:   Name of the file to write to
'''
def write_file(data, filename):
    byteStr = ''
    for byte in data:
        byteStr += chr(byte)

    f = open(filename, "wb")
    try:
        f.write(byteStr)
    finally:
        f.close()

'''
*   Translates an integer to a list of bits
*       num:    The integer that will be translated
*       return: A list of bits
'''
def int_to_bin(num):
    bits = []
    while num != 0:
        bit = num % 2
        num /= 2
        bits.append(bit)
    while (len(bits) == 0) or (len(bits) % 8 != 0):
        bits.append(0)
    return bits


'''
*   Translates a list of bits into an integer
*       data:   A list of bits
*       return: An integer
'''
def bin_to_int(data):
    num = 0
    for i in range(len(data)):
        if (data[i] == 1): num += (2 ** i)
    return num

'''
*   Translates the list of bytes to an list of bits
*       data:   A list of bytes
*       return: An list of bits
'''
def byte_to_bin(data):
    bits = []
    for byte in data:
        bits += int_to_bin(byte)

    return bits

'''
*   Translates list of bytes to a string of bits
*       data:   An list of bits
*       return: An list of bytes
'''
def bin_to_bytes(data):
    bytes = []
    bits = [0]*8

    # Iterate through all of the bits and translate them into bytes one byte at a time
    for i in range(len(data)):
        if (i%8 == 0 and i != 0):
            byte = bin_to_int(bits)
            bytes.append(byte)
        bits[i%8] = data[i]

    # The loop doesn't handle the very last byte of bits so we do it here
    byte = bin_to_int(bits)
    bytes.append(byte)

    return bytes

'''
*   Hides binary data in an image's pixels
*       data:       List of bits
*       imageName:  Name of the image we intend on hiding the bits in
*       output:     Name of the new image to create
'''
def hide_data(data, imageName, output):
    # Open the image and extract the pixels as well as the size
    img = Image.open(imageName)
    pixels = img.load()
    y, x = img.size

    # This next section stores the length of the data into the first row of the image's red values
    # First create an list to store into the first row
    length = len(data)
    firstRow = [0] * x
    lengthBits = int_to_bin(length)
    for i in range(0, len(lengthBits)):
        firstRow[i] = lengthBits[i]

    # Next actually store the new list into the first row of the image
    for i in range(x):
        r,_,_,_ = pixels[0, i]
        if (firstRow[i] != r%2):
            r += 1
        pixels[0, i] = r,_,_,_

    # Setup to store the actual data in the message
    row = 1                     # counter for our cols
    col = 0                     # counter for our rows
    r,g,b,_ = pixels[row, col]  # first values to edit

    # Loop through flipping bits appropriately until we run out of data
    for i in range(length):
        if (i%3 == 0):
            if (r%2 != data[i]): r += 1
        if (i%3 == 1):
            if (g%2 != data[i]): g += 1
        if (i%3 == 2):
            if (b%2 != data[i]): b += 1

        # Store the new values back where they came from
        # We must do this every time because we don't know if our data is a multiple of 3
        pixels[row, col] = r,g,b,_

        # If i%3 is 2 than we've written the entire pixels
        # Therefore we should move on to the next one
        if (i%3 == 2):
            col += 1
            if (col >= x):
                col = 0
                row += 1
            r,g,b,_ = pixels[row, col]


    # Save the image and close
    img.save(output)
    img.close()

'''
*   Extracts binary data hidden in an image
*       imageName:  Name of the image to extract the data from
*       return:     List of binary data
'''
def unhide_data(imageName):
    # Open the image and extract the pixels as well as the size
    img = Image.open(imageName)
    pixels = img.load()
    y, x = img.size

    # Get the length from the first row of the image
    lengthBits = []
    for i in range(x):
        r,_,_,_ = pixels[0,i]
        lengthBits.append(r%2)
    length = bin_to_int(lengthBits)


    # Set up to read from the file
    bits = []
    row = 1
    col = 0
    r,g,b,_ = pixels[row,col]

    # Continue reading from the pixels until we get all the data
    for i in range(length):
        if (i%3 == 0):   bits.append(r%2)
        if (i%3 == 1):   bits.append(g%2)
        if (i%3 == 2):   bits.append(b%2)

        # If we've read from the entire pixel move to the next
        if (i%3 == 2):
            col += 1
            if (col >= x):
                col = 0
                row += 1
        r,g,b,_ = pixels[row,col]


    # Close the image and return the data
    img.close()
    return bits

'''
*   Just a compact procedure for hiding in an image
'''
def hide(src, img, out):
    print "Hiding " + src + " in " + img + "..."
    data = read_file(src)
    bits = byte_to_bin(data)
    hide_data(bits, img, out)
    print "Succesfully hidden in " + out

'''
*   Just a compact procedure for unhiding from an image
'''
def unhide(img, out):
    print "Reading from " + img + "..."
    bits = unhide_data(img)
    data = bin_to_bytes(bits)
    write_file(data, out)
    print "Data written to " + out + "..."

'''
*   Processes the command line arguments
*       argv:   The command line arguments not including index 0
*       return: The file names for the source file, image file, and output file
*   NOTE: If an image is provided without a source we assume we're reading out from the image
'''
def process_cmd(argv):
    src = ""
    img = ""
    out = "output"
    operation = "hide"
    try:
        opts, args = getopt.getopt(argv, "hs:i:o:", [])
    except getopt.GetoptError:
        print "stego.py -s <source_file>  -i <image_file> -o <output_file>"
        sys.exit(2)

    for opt, arg in opts:
        if (opt == '-h'):
            print_help()
            operation = None
            return (None, None, None, None)
        elif (opt == "-s"):
            src = arg
        elif (opt == "-i"):
            img = arg
        elif (opt == "-o"):
            out = arg

    if (img == ""):
        print "stego.py -s <source_file>  -i <image_file> -o <output_file>"
        sys.exit(2)
    else:
        if (src == ""):
            operation = "unhide"
        else:
            if (out[-4:] != ".png"):
                out += ".png"

    return (src, img, out, operation)

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
            src = raw_input('  source file: ')
            img = raw_input('  image file: ')
            out = raw_input('  output name: ')

            # Hide the message in the image
            hide(src,img,out)
        elif (userInput == 'unhide' or userInput == 'u'):
            # Get the image and output file names
            img = raw_input('  image file: ')
            out = raw_input('  output file: ')

            # Unhide the image
            unhide(img, out)
        elif (userInput == "help"):
            print_help()
        elif (userInput != 'quit' and userInput != 'q'):
            print('[X] Unknown Command: ' + userInput)
            print_help()

'''
*   Just Prints The Help Information
'''
def print_help():
    print("-------------------------------------")
    print("|My Super Duper Steganography Script|")
    print("-------------------------------------")
    print('\nCommand Line: ')
    print('  stego.py -s <source_file>  -i <image_file> -o <output_file>')
    print("\nUser interface: ")
    print('  (h)ide:    Hide a message')
    print('  (u)nhide:  Unhide a message')
    print('  (q)uit:    Stops the program')
    print('  help:      Prints this help message')
    print('  Example:\n     Command :-$ hide\n')

def main():
    if (len(sys.argv) == 1):
        user_interface()
        return

    argv = sys.argv[1:]
    src, img, out, operation = process_cmd(argv)

    if (operation == "hide"):
        hide(src, img, out)
    elif (operation == "unhide"):
        unhide(img, out)

main()
