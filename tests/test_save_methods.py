import unittest

from pandas import DataFrame
from PyMD import MDGenerator


class SavingFiles(unittest.TestCase):
    mdGen = None

    def setup(self):
        if self.mdGen is not None:
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
        self.mdGen = mdGen

    def test_json(self):
        self.setup()
        self.mdGen.save_json()

        with open("example/GeneratedMD.json", "r") as f:
            data = f.read()
            self.assertIn("Section 1", data)
            self.assertIn("Section 2", data)
            self.assertIn("Section 3", data)
            self.assertIn("Subsection 1", data)
            self.assertIn("Subsection 2", data)
            self.assertIn("Subsubsection 1", data)
            self.assertIn("This is the first section.", data)
            self.assertIn("This is the second section.", data)
            self.assertIn("print('Hello, World!')", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsubsection of the second subsection.", data)
            self.assertIn("This is a random figure.", data)
            self.assertIn("Item 1", data)
            self.assertIn("Item 2", data)
            self.assertIn("Item 3", data)
            self.assertIn("https://www.google.com", data)
            self.assertIn("Google", data)
            self.assertIn("Check 1", data)
            self.assertIn("Check 2", data)
            self.assertIn("Check 3", data)
            self.assertIn("Header 1", data)
            self.assertIn("Header 2", data)
            self.assertIn("Header 3", data)
            self.assertIn("Header 4", data)
            self.assertIn("Numpy Array Table", data)
            self.assertIn("Python List Table", data)
            self.assertIn("Pandas DataFrame Table", data)
            self.assertIn("This is a random figure.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsection of the first section.", data)
            self.assertIn("This is a subsubsection of the second subsection.", data)
            self.assertIn("This is a random figure.", data)
            self.assertIn("Item 1", data)
            self.assertIn("Item 2", data)
            self.assertIn("Item 3", data)
            self.assertIn("https://www.google.com", data)
            self.assertIn("Google", data)
            self.assertIn("Check 1", data)
            self.assertIn("Check 2", data)
            self.assertIn("Check 3", data)
            self.assertIn("Header 1", data)
            self.assertIn("Header 2", data)

    def test_load_json(self):
        self.setup()
        self.mdGen.save_json()
        mdGen = MDGenerator("/home/rlfowler/Documents/myprojects/PyMD/example", file_name='GeneratedMD', title="Generated Markdown", author="Author")
        mdGen.load_json()

        self.assertListEqual(self.mdGen.section_headers, mdGen.section_headers)
        self.assertDictEqual(self.mdGen.section_type_count, mdGen.section_type_count)


if __name__ == "__main__":
    unittest.main()
            