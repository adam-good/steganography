'''
*       Name:   stego.py
*       Author: Adam Good
*
*       Description:
*           Just a simple steganography script. It currently can hide a 
*           message (from a file) into the red values of the pixels of an
*           image. Just some afternoon fun I had. Will improve later.
*
*       TODO:
*           Store message in every color of pixel, not just red
*           Better UI
*           Clean the code
*           Make it able to store any stort of payload, not just text
'''

from PIL import Image

# Convert the message to binary
def getBits(msg):
    bits = []
    bytes = (ord(b) for b in msg) # Get the decimal value of each byte
    for b in bytes:
        for i in xrange(8):
            bits.append((b >> i) & 1) # Append the bits to the list of bits (might describe this more in depth later for those who don't understand bitwise operations)
    return bits

def hideMsg(img, msg):
    # img should already be open. Load the pixels and get the dimensions
    pxls = img.load()
    rows,cols = img.size

    # Ensure the length of the message is suitable
    l = len(msg)
    # If the message length can't be stored in the first row
    if (l*8 >= 2**rows):
        print ("[X] Message so big we can't even store the length of it correctly...")
    # If the message has more bits than the image has pixels
    if (l*8 > rows*cols):
        print ("[X] Message to big for the image! Sorry!!")
        return None
    
    # Convert the length to bits
    bits = [0] * rows
    for i in xrange(rows):
        bits[i] = (l >> i) & 1
    
    # Store the bits in the first row of the image    
    for x in xrange(rows):
        r,g,b = pxls[x,0]
        if (r%2 != bits[x]):
            r += 1
        pxls[x,0] = (r,g,b)
    
    # Get the bits of the actual message. Also Initialize the coordinate variables we'll use
    # Remember we start y at 1 because y=0 is where we stored the message length
    bits = getBits(msg)
    x = 0
    y = 1
    # Loop through all of our bits
    for bit in bits:
        # Edit the pixels so that they contain our message
        r,g,b = pxls[x,y]   # get the pixel values
        if (bit != (r%2)):  # If the least significant bit is not correct we flip it
            r += 1
        pxls[x,y] = (r,g,b) # Assign the new value to our pixel
        
        # Increment our coordinates in the correct order
        x += 1
        if (x >= rows):
            x = 0
            y += 1

    # Save the new image and notify the user
    secretImage = "img_msg.png" 
    img.save(secretImage)
    print "[*] Message hidden in " + secretImage
    
# This will get a message from an image
def readMsg(img):
    # Load the pixels and get the dimensions
    pxls = img.load()
    rows,cols = img.size

    # First we get the length of the message stored in the first row
    length = 0
    for i in range(rows):
        r,g,b = pxls[i,0]
        if (r%2 == 1):
            length += 2**i
    length *= 8 # Multiply the length by 8 because length is in units of bytes but we are working with bits (8bits=1byte)
    
    msg = ''    # msg will store the message
    c = 0       # this will store the decimal value of each byte
    i = 0       # this will be our counter so we know when we've read an entire byte
    
    # These loops iterate through the pixels starting from the second row
    for y in range(1,cols):
        for x in range(rows):
            r,g,b = pxls[x,y]   # get the values from the pixel
            if ((r%2) == 1):    # Convert from binary to decimal one bit at a time
                c += 2 ** i
            length -= 1         # decrement length so we can check when the message is finished
            i += 1              # keep track of bits
            # if we've read an entire byte(8 total bits) we append the character to message and reset variables
            if (i > 7):
                msg = msg + chr(c)
                c = 0
                i = 0
            # If we've read the entire message we return it
            if (length == 0):
                return msg

# main is just a simple menu function where the program starts. It's the UI.
# Not gonna bother commenting at the moment, but I probably will later
def main():
    userInput = 'who cares'
    while (userInput != '0'):
        print("1.) Hide a message")
        print("2.) Unhide a message")
        print("0.) quit")
        userInput = raw_input("Command :-$ ")
        if (userInput == '1'):
            msg = open(raw_input("message file: ")).read()
            imgName = raw_input("image name: ")
            img = Image.open(imgName)
            hideMsg(img, msg)
            img.close()
        elif (userInput == '2'):
            imgName = raw_input("image name: ")
            img = Image.open(imgName)
            print ("[*] Begin Message:\n")
            print readMsg(img)
#            print ("[*] End Message\n")
            raw_input("[*] End Message")
        elif (userInput != '0'):
            print ("Invalid Input")
            userInput = 'who cares'

main()
