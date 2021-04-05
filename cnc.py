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
    
    @staticmethod
    def parse_from_file(path):
        with open(path) as gcode_file:
            return Program.parse(gcode_file.read())
    
    @staticmethod
    def parse(data):
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
        """Run the blocks of the program sequentially"""
        print(self.number)
        print("-------------")
        for b in self.blocks:
            b.run(machine_client)

class Block:
    def __init__(self, number, words):
        self.number = number
        self.words = words

    @staticmethod
    def parse(data):
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
        return Block(block_number, words)
    
    def run(self, machine_client):
        """Run the words of the block"""
        # TODO: execution order
        for w in self.words:
            if w.letter == "S":
                # spindle speed
                machine_client.set_spindle_speed(w.number)
            elif w.letter == "F":
                # feed rate
                machine_client.set_feed_rate(w.number)
            elif w.letter == "T":
                # tool
                machine_client.change_tool(w.number)
            print("{}: {}".format(w.letter, w.number))
        print("-------------")
        
class Word:
    def __init__(self, letter, number):
        self.letter = letter
        self.number = number

    @staticmethod
    def parse(command):
        if command.startswith("X") or command.startswith("Y") or command.startswith("Z") or command.startswith("F"):
            return Word(command[0], float(command[1:]))
        elif command.startswith("T"):
            return Word(command[0], command[1:])
        else:
            return Word(command[0], int(command[1:]))

def parse_arguments():
    arguments = []
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
    return arguments

files = parse_arguments()

for file in files:
    program = Program.parse_from_file(file)
    client = MachineClient()
    program.run(client)
