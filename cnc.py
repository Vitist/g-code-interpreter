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
        blocks = []
        program_start = False
        for line in data.splitlines():
            if line.startswith("%"):
                program_start = not program_start
            elif program_start:
                blocks.append(line)
                print(line)
        return Program(1, blocks)
    
    def run(self):
        """Run the blocks of the program sequentially"""
        print(self.number)
        print(self.blocks)

class Block:
    def __init__(self, number, words):
        self.number = number
        self.words = words
        
    def run(self):
        """Run the words of the block sequentially"""
        pass
        
class Word:
    def parse(self, command):
        pass
     
def parse_arguments():
    arguments = []
    if len(sys.argv) > 1:
        arguments = sys.argv[1:]
    return arguments

files = parse_arguments()

for file in files:
    program = Program.parse_from_file(file)
    program.run()
