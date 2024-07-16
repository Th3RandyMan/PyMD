from time import sleep
import unittest

from PyMD import MDGenerator
from pandas import DataFrame


class IndexingMethods(unittest.TestCase):
    mdGen = None

    def setup(self):
        self.mdGen = MDGenerator("example", title="Generated Markdown", author="Author")
        

    def test_single_bracketing(self):
        self.setup()
        self.mdGen["Section 1"].add_text("This is the first section.")
        self.mdGen["Section 2"].add_text("This is the second section.")
        self.mdGen["Section 2"].add_code("print('Hello, World!')")
        self.mdGen["Section 3"]["Subsection 1"].add_text("This is a subsection of the first section.")
        self.mdGen["Section 3"]["Subsection 2"].add_text("This is a subsection of the first section.a")
        self.mdGen["Section 3"]["Subsection 2"]["Subsubsection 1"].add_text("This is a subsubsection of the second subsection.")
        self.mdGen["Section 3"]["Subsection 2"]["Subsubsection 1"].add_text("This is a subsubsection of the second subsection.a")
        self.mdGen["Section 3"]["Subsection 2"]["Subsubsection 1"].add_text("This is a subsubsection of the second subsection.b")
        self.mdGen["Section 4"]["Subsection 1a"]["Subsubsection 1a"]["Subsubsubsection 1a"].add_text("This is a subsubsubsection of the second subsection.abc")

        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Section 1", data)
            self.assertIn("Section 2", data)
            self.assertIn("Section 3", data)
            self.assertIn("Subsection 1", data)
            self.assertIn("Subsection 2", data)
            self.assertIn("Subsection 1a", data)
            self.assertIn("Subsubsection 1", data)
            self.assertIn("Subsubsection 1a", data)
            self.assertIn("Subsubsubsection 1a", data)

            self.assertIn("This is the first section.", data)
            self.assertIn("This is the second section.", data)
            self.assertIn("print('Hello, World!')", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsection of the first section.a", data)
            self.assertIn("This is a subsubsection of the second subsection.", data)
            self.assertIn("This is a subsubsection of the second subsection.a", data)
            self.assertIn("This is a subsubsection of the second subsection.b", data)
            self.assertIn("This is a subsubsubsection of the second subsection.abc", data)

    def test_multi_bracketing(self):
        self.setup()
        self.mdGen["Section 1/Subsection 1/Subsubsection 1"].add_text("This is a subsubsection of the first section.")
        self.mdGen["Section 1/Subsection 1/Subsubsection 1"].add_text("This is a subsubsection of the first section.a")
        self.mdGen["Section 2/Subsection 1a/Subsubsection 1a"].add_text("This is a subsubsection of the first section.b")
        self.mdGen["Section 2/Subsection 1a/Subsubsection 1a/meh"].add_text("This is a subsubsection of the first section.c")

        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Section 1", data)
            self.assertIn("Section 2", data)
            self.assertIn("Subsection 1", data)
            self.assertIn("Subsection 1a", data)
            self.assertIn("Subsubsection 1", data)
            self.assertIn("Subsubsection 1a", data)
            self.assertIn("meh", data)

            self.assertIn("This is a subsubsection of the first section.", data)
            self.assertIn("This is a subsubsection of the first section.a", data)
            self.assertIn("This is a subsubsection of the first section.b", data)
            self.assertIn("This is a subsubsection of the first section.c", data)

    def test_empty_subsections(self):
        self.setup()
        self.mdGen["Section 1//Subsubsection 1"].add_text("This is a subsubsection of the first section.")
        self.mdGen["Section 1//Subsubsection 1"].add_text("This is a subsubsection of the first section.a")
        self.mdGen["Section 2/Subsection 1a/"].add_text("This is a subsubsection of the first section.b")
        self.mdGen["/Subsection 1a/Subsubsection 1a"].add_text("This is a subsubsection of the first section.c")
        self.mdGen["Section 2/Subsection 1a///meh"].add_text("This is a subsubsection of the first section.d")
        self.mdGen["Section 3"][""][""].add_text("This is a subsubsection of the first section.e")

        self.mdGen.save()

        with open("example/GeneratedMD.md", "r") as f:
            data = f.read()
            self.assertIn("Section 1", data)
            self.assertIn("Section 2", data)
            self.assertIn("Section 3", data)
            self.assertIn("Subsection 1a", data)
            self.assertIn("Subsubsection 1", data)
            self.assertIn("Subsubsection 1a", data)
            self.assertIn("meh", data)

            self.assertIn("This is a subsubsection of the first section.", data)
            self.assertIn("This is a subsubsection of the first section.a", data)
            self.assertIn("This is a subsubsection of the first section.b", data)
            self.assertIn("This is a subsubsection of the first section.c", data)
            self.assertIn("This is a subsubsection of the first section.d", data)
            self.assertIn("This is a subsubsection of the first section.e", data)

    # def test_empty_base(self)


if __name__ == '__main__':
    unittest.main()