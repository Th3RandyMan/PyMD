from time import sleep
import unittest

from pandas import DataFrame
from PyMD.MDGenerator import MDGenerator


class AssignmentTypes(unittest.TestCase):
    mdGen = None

    def setup(self):
        self.mdGen = MDGenerator("example", title="Generated Markdown", author="Author")
        

    def test_string_assignment(self):
        raise NotImplementedError

    def test_figure_assignment(self):
        raise NotImplementedError

    def test_dataframe_assignment(self):
        raise NotImplementedError

    def test_numpy_array_assignment(self):
        raise NotImplementedError