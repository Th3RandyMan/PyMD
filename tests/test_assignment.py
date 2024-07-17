from time import sleep
import unittest

from pandas import DataFrame
from PyMD import MDGenerator
from matplotlib import pyplot as plt
import numpy as np


class AssignmentTypes(unittest.TestCase):
    mdGen = None

    def setup(self):
        self.mdGen = MDGenerator("example", title="Generated Markdown", author="Author")
        

    def test_string_assignment(self):
        self.setup()
        self.mdGen["Section 1"] = "This is the first section."
        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("This is the first section.", data)

    def test_figure_assignment(self):
        self.setup()

        # Create a random figure
        fig, ax = plt.subplots()
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        ax.plot(x, y)
        self.mdGen["Section 1"] = fig
        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("figures/GeneratedMD_image0.png", data)

    def test_dataframe_assignment(self):
        self.setup()

        # Create a random table
        headers = ["Header 1", "Header 2", "Header 3", "Header 4"]
        table = np.random.randint(0, 10, (6, 4))
        df = DataFrame(table, columns=headers)
        self.mdGen["Section 1"] = df
        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Header 1", data)
            self.assertIn("Header 2", data)
            self.assertIn("Header 3", data)
            self.assertIn("Header 4", data)

    def test_numpy_array_assignment(self):
        self.setup()

        # Create a random table
        table = np.random.randint(0, 10, (6, 4))
        self.mdGen["Section 1"] = table
        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Column 1", data)
            self.assertIn("Column 2", data)
            self.assertIn("Column 3", data)
            self.assertIn("Column 4", data)

    def test_list_assignment(self):
        self.setup()

        # Create a random list
        lst = ["Item 1", "Item 2", "Item 3"]
        self.mdGen["Section 1"] = lst
        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Item 1", data)
            self.assertIn("Item 2", data)
            self.assertIn("Item 3", data)