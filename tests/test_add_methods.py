from time import sleep
import unittest

from pandas import DataFrame
from PyMD import MDGenerator


class AddingRandomStuff(unittest.TestCase):
    setup_done = False

    def setup(self):
        if self.setup_done:
            return
        
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


        # Add a table to the markdown file
        headers = ["Header 1", "Header 2", "Header 3", "Header 4"]
        table = np.random.randint(0, 10, (6, 4))
        df = DataFrame(table, columns=headers)
        
        list_table = ["Header 1", "Header 2", "Header 3"] + [str(3*i + j) for i in range(3) for j in range(3)]
        # mdGen.add_table("Section 3/Numpy Array Table", table)
        mdGen["Section 3"]["Numpy Array Table"].add_table(table)
        # mdGen.add_table("Section 3/Python List Table", list_table, 3, 4)
        mdGen["Section 3"]["Python List Table"].add_table(list_table, 3, 4)
        # mdGen.add_table("Section 3/Pandas DataFrame Table", df)
        mdGen["Section 3"]["Pandas DataFrame Table"].add_table(df)

        # Save the markdown file
        mdGen.save()
        self.setup_done = True

    def test_add_text(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("This is the first section.", data)
            self.assertIn("This is the second section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsubsection of the second subsection.", data)

    def test_add_code(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("```python\nprint('Hello, World!')\n```", data)

    def test_add_image(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("This is a random figure.", data)

    def test_add_list(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("- Item 1\n- Item 2\n- Item 3", data)

    def test_add_link(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("[Google](https://www.google.com)", data)

    def test_add_checkbox(self):
        self.setup()
        with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
            data = file.read()
            self.assertIn("- [x] Check 1  \n- [ ] Check 2  \n- [x] Check 3  ", data)

    # def test_add_table(self):
    #     self.setup()
    #     with open("/home/rlfowler/Documents/myprojects/PyMD/example/GeneratedMD.md", "r") as file:
    #         data = file.read()
    #         self.assertIn("|Header 1|Header 2|Header 3|Header 4|\n|---|---|---|---|\n|0|3|2|4|\n|9|0|5|2|\n|3|9|7|6|\n|9|3|5|5|\n|0|5|2|5|\n|4|6|3|9|", data)
    #         self.assertIn("|Header 1|Header 2|Header 3|Header 4|\n|---|---|---|---|\n|Header 1|Header 2|Header 3|0|\n|1|2|3|3|\n|4|5|6|4|\n|7|8|0|5|", data)
    #         self.assertIn("|Header 1|Header 2|Header 3|Header 4|\n|---|---|---|---|\n|0|1|2|3|\n|4|5|6|7|\n|8|9|0|1|\n|2|3|4|5|\n|6|7|8|9|", data)
            
    # def test_add_multiple_images(self):



if __name__ == '__main__':
    unittest.main()