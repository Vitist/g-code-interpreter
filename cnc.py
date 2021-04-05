import sys
import os

class MachineClient:
    def home(self):
        """ Moves machine to home position. """
        print("Moving to home.")

    def move(self, x, y, z):
        """ Uses linear movement to move spindle to given XYZ coordinates.
        Args:
        x (float): X axis absolute value [mm]
        y (float): Y axis absolute value [mm]
        z (float): Z axis absolute value [mm]
        """
        print("Moving to X={:.3f} Y={:.3f} Z={:.3f} [mm].".format(x, y, z))

    def move_x(self, value):
        """ Move spindle to given X coordinate. Keeps current Y and Z unchanged.
        Args:
        value (float): Axis absolute value [mm]
        """
        print("Moving X to {:.3f} [mm].".format(value))
 
    def move_y(self, value):
        """ Move spindle to given Y coordinate. Keeps current X and Z unchanged.
        Args:
        value(float): Axis absolute value [mm]
        """
        print("Moving Y to {:.3f} [mm].".format(value))

    def move_z(self, value):
        """ Move spindle to given Z coordinate. Keeps current X and Y unchanged.
        Args:
        value (float): Axis absolute value [mm]
        """
        print("Moving Z to {:.3f} [mm].".format(value))
 
    def set_feed_rate(self, value):
        """ Set spindle feed rate.
        Args:
        value (float): Feed rate [mm/s]
        """
        print("Using feed rate {} [mm/s].".format(value))
 
    def set_spindle_speed(self, value):
        """ Set spindle rotational speed.
        Args:
        value (int): Spindle speed [rpm]
        """
        print("Using spindle speed {} [mm/s].".format(value))
 
    def change_tool(self, tool_name):
        """ Change tool with given name.
        Args:
        tool_name (str): Tool name.
        """
        print("Changing tool '{:s}'.".format(tool_name))
 
    def coolant_on(self):
        """ Turns spindle coolant on. """
        print("Coolant turned on.")
 
    def coolant_off(self):
        """ Turns spindle coolant off. """
        print("Coolant turned off.")

class Program:
    def __init__(self, number, blocks):
        self.number = number
        self.blocks = blocks
        self.tool = ""
        self.x = float(0)
        self.y = float(0)
        self.z = float(0)
    
    @staticmethod
    def parse_from_file(path):
        """ Parse a G-code program from a file.
        Args:
        path (string): Path to G-code file
        """
        with open(path) as gcode_file:
            return Program.parse(gcode_file.read())
    
    @staticmethod
    def parse(data):
        """ Parse a G-code program from a string of G-code commands.
        Args:
        data (string): contents of a G-code file
        """
        program_number = -1
        blocks = []
        program_start = False
        for line in data.splitlines():
            # Strip comments out of the block
            stripped_line = ""
            comment = False
            for c in line:
                if c == "(":
                    comment = True
                elif c == ")":
                    comment = False
                elif not comment:
                    stripped_line += c
            # Remove all whitespace
            stripped_line = "".join(stripped_line.split())
            
            if len(stripped_line) > 0:
                if stripped_line.startswith("%"):
                    program_start = not program_start
                elif program_start:
                    if line.startswith("O"):
                        if line[1:].isdigit():
                            program_number = int(line[1:])
                        else:
                            print("Invalid program number {}.".format(line[1:]))
                    else:
                        blocks.append(Block.parse(stripped_line))
        return Program(program_number, blocks)
    
    def run(self, machine_client):
        """Run the blocks of the program sequentially
        Args:
        machine_client (MachineClient): MachineClient object that is used to control the CNC machine
        """
        for b in self.blocks:
            self.tool, self.x, self.y, self.z = b.run(machine_client, self.tool, self.x, self.y, self.z)

class Block:
    def __init__(self, number, words):
        self.number = number
        self.words = words

    @staticmethod
    def parse(data):
        """ Parse a G-code program block from a string of G-code commands.
        Args:
        data (string): A single line of a G-code program
        """
        block_number = -1
        words = []
        letters = ("N", "G", "T", "S", "M", "X", "Y", "Z", "F")
        command = ""
        for c in data:
            if c in letters:
                if len(command) > 0:
                    word = Word.parse(command)
                    # Block number should be at the start of the block
                    if word.letter == "N":
                        block_number = word.number
                    else:
                        words.append(word)
                command = c
            else:
                command += c
        words.append(Word.parse(command))
        words.sort(key=lambda w: w.priority)
        return Block(block_number, words)
    
    def run(self, machine_client, tool, x, y, z):
        """Run the words of the block
        Args:
        machine_client (MachineClient): MachineClient object that is used to control the CNC machine
        tool (string): Currently selected tool
        x (float): Current X axis absolute value [mm]
        y (float): Current Y axis absolute value [mm]
        z (float): Current Z axis absolute value [mm]
        """
        for w in self.words:
            if w.letter == "S":
                # Spindle speed
                machine_client.set_spindle_speed(w.number)
            elif w.letter == "F":
                # Feed rate
                machine_client.set_feed_rate(w.number)
            elif w.letter == "T":
                # Select tool
                tool = w.number
            elif w.letter == "M":
                if w.number == 3 or w.number == 4:
                    # Start spindle (3 clockwise, 4 counterclockwise)
                    pass
                elif w.number == 5:
                    # Stop spindle
                    pass
                elif w.number == 6:
                    # Change tool
                    machine_client.change_tool(tool)
                elif w.number == 7 or w.number == 8:
                    # Coolant on (7 mist, 8 flood)
                    machine_client.coolant_on()
                elif w.number == 9:
                    # Coolant off
                    machine_client.coolant_off()
                elif w.number == 30:
                    # End program
                    pass
            elif w.letter == "G":
                if w.number == 0 or w.number == 1:
                    # Move (0 fast, 1 linear)
                    # Find coordinate words from block
                    move_x = False
                    move_y = False
                    move_z = False
                    for cw in self.words:
                        if cw.letter == "X":
                            x = cw.number
                            move_x = True
                        elif cw.letter == "Y":
                            y = cw.number
                            move_y = True
                        elif cw.letter == "Z":
                            z = cw.number
                            move_z = True
                    # Move linearly on multiple axis if coordinates for atleast
                    # 2 axis were given, else move on a single axis.
                    if (move_x and move_y) or (move_x and move_z) or (move_y and move_z):
                        machine_client.move(x, y, z)
                    elif move_x:
                        machine_client.move_x(x)
                    elif move_y:
                        machine_client.move_y(y)
                    elif move_z:
                        machine_client.move_z(z)
                elif w.number == 17:
                    # XY plane selection
                    pass
                elif w.number == 21:
                    # Programming in millimeters
                    pass
                elif w.number == 28:
                    # Move to home
                    x = float(0)
                    y = float(0)
                    z = float(0)
                    machine_client.home()
                elif w.number == 40:
                    # Tool radius compensation off
                    pass
                elif w.number == 49:
                    # Tool length offset compensation cancel
                    pass
                elif w.number == 80:
                    # Cancel canned cycle
                    pass
                elif w.number == 91:
                    # Incremental programming
                    pass
                elif w.number == 94:
                    # Fixed cycle, simple cycle, for roughing
                    pass
        return tool, x, y, z
        
class Word:
    def __init__(self, letter, number, priority):
        self.letter = letter
        self.number = number
        self.priority = priority
        
    @staticmethod
    def parse(command):
        """ Parse a G-code program word from a string.
        Args:
        data (string): A single word of a G-code program
        """
        letter = command[0]
        
        # Parse number from word
        if letter == "X" or letter == "Y" or letter == "Z" or letter == "F":
            number = float(command[1:])
        elif command.startswith("T"):
            number = command[1:]
        else:
            number = int(command[1:])
        
        # Set word priority, order of execution from http://linuxcnc.org/docs/html/gcode/overview.html
        if letter == "F":
            priority = 1
        elif letter == "S":
            priority = 2
        elif letter == "T":
            priority = 3
        elif letter == "M" and number == 6:
            priority = 4
        elif letter == "M" and (number == 3 or number == 4 or number == 5):
            priority = 5
        elif letter == "M" and (number == 7 or number == 8 or number == 9):
            priority = 6
        elif letter == "G" and number == 28:
            priority = 7
        elif letter == "G" and (number == 0 or number == 1):
            priority = 8
        elif letter == "M" and number == 30:
            priority = 9
        else:
            priority = 10
        
        return Word(letter, number, priority)

def parse_arguments():
    """ Parse command line arguments."""
    arguments = []
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
    return arguments

# Parse G-code file paths from arguments
files = parse_arguments()
# Parse G-code programs from the files and run them
for file in files:
    program = Program.parse_from_file(file)
    client = MachineClient()
    program.run(client)
