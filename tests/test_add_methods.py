from time import sleep
import unittest
from PyMD.MDGenerator import MDGenerator


class AddingRandomStuff(unittest.TestCase):
    def setup(self):
        mdGen = MDGenerator("/home/rlfowler/Documents/myprojects/PyMD/example", file_name='GeneratedMD', title="Generated Markdown", author="Author")
        mdGen.add_text("Section 1", "This is the first section.")
        mdGen.add_text("Section 2", "This is the second section.")
        mdGen.add_code("Section 2", "print('Hello, World!')")
        mdGen.add_text("Section 1/Subsection 1", "This is a subsection of the first section.")
        mdGen.add_text("Section 1/Subsection 2", "This is a subsection of the first section.")
        mdGen.add_text("Section 1/Subsection 2/Subsubsection 1", "This is a subsubsection of the second subsection.")

        import matplotlib.pyplot as plt
        import numpy as np

        # Generate random data
        x = np.linspace(0, 10, 100)
        y = np.random.randn(100)

        # Create a figure and plot the data
        fig, ax = plt.subplots()
        ax.plot(x, y)

        # Add labels and title
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_title('Random Figure')

        # Add the image to the markdown file
        mdGen.add_image("Section 1", fig, "This is a random figure.")

        # Add a list to the markdown file
        mdGen.add_list("Section 2", ["Item 1", "Item 2", "Item 3"])

        # Add a link to the markdown file
        mdGen.add_link("Section 2", "https://www.google.com", "Google")

        # Add a checkbox list to the markdown file
        mdGen.add_checkbox("Section 2", ["Check 1", "Check 2", "Check 3"], [True, False, True])

        # Save the markdown file
        mdGen.save()
        sleep(1)

    def test_add_text(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("This is the first section.", data)
            self.assertIn("This is the second section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsubsection of the second subsection.", data)

    def test_add_code(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("```python\nprint('Hello, World!')\n```", data)

    def test_add_image(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("This is a random figure.", data)

    def test_add_list(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("- Item 1\n- Item 2\n- Item 3", data)

    def test_add_link(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("[Google](https://www.google.com)", data)

    def test_add_checkbox(self):
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("- [x] Check 1\n- [ ] Check 2\n- [x] Check 3", data)



if __name__ == '__main__':
    unittest.main()