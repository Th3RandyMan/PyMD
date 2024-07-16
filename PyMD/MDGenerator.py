"""
To do:
    - Add subsections to list
    - Add section links/references
"""
import json
from matplotlib.figure import Figure
from mdutils.mdutils import MdUtils
from pathlib import Path
from typing import Dict, Optional, Union, List
from .tools.utils import is_file_type, FIGURE_FOLDER
from .tools.sections import *


class MDGenerator(Section):
    """
    Markdown Generator class to generate markdown files.
    """
    def __init__(self, save_path: Optional[Union[str,Path]] = None, file_name:str = "GeneratedMD", title:Optional[str] = None, author:Optional[Union[str,List[str]]] = None, dpi:Optional[int] = None):
        """
        Initialize the markdown generator.

        Args:
            save_path (Optional[Union[str,Path]], optional): Path to save the generated file. If None, the current working directory is used.
            file_name (str, optional): Name of the generated file. Defaults to "GeneratedMD".
            title (str, optional): Title of the document. Defaults to None.
            author (str, optional): Author of the document. Defaults to None.
            dpi (int, optional): DPI of the generated image. Defaults to None, figures dpi.
        """
        if save_path is None:
            self.save_path = Path.cwd()
        elif isinstance(save_path, str):
            if is_file_type(save_path):
                file_name = ".".join(save_path.split("/")[-1].split(".")[:-1])
                save_path = "/".join(save_path.split("/")[:-1])
            self.save_path = Path(save_path)
        elif isinstance(save_path, Path):
            self.save_path = save_path
        else:
            raise TypeError("save_path must be a str or Path object")

        self.save_path.mkdir(parents=True, exist_ok=True)

        self.file_name = file_name
        if title is None:
            self.title = ""
        else:
            self.title = title
        if author is None:
            self.author = ""
        else:
            if isinstance(author, list):
                self.author = "Authors: " + ", ".join(author)
            else:
                self.author = f"Author: {author}"
        
        self.dpi = dpi  # Store dpi for the figures
        
        mdFile = MdUtils(file_name=str(self.save_path / (file_name + ".md")), title=self.title, author=self.author)
        self.section_headers:List[str] = []
        self.section_type_count:Dict[SectionType,int] = SectionType.new_dictionary(SectionType)
        
        # Set the class variables for the Section class
        Section.save_path = self.save_path
        Section.dpi = self.dpi
        Section.section_headers = self.section_headers
        Section.section_type_count = self.section_type_count

        # Initialize the Parent Section class
        Section.__init__(self, mdFile)

    def section_search(self, key:str) -> Section:
        """
        Search for the section with the given key.
        
        Args:
            key (str): Key to search for.

        Returns:
            Optional[BaseSection]: Section with the given key.
        """
        if len(key) > 0 and key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        
        ptr = self
        for k in keys:
            ptr = ptr[k]
        return ptr
            
    def add_text(self, header:Optional[str]=None, text:str="\n") -> BaseSection:
        """
        Add a text section to the markdown file.

        Args:
            header (str): Header of the section.
            text (str): Text of the section.
        """
        if header is None:
            super().add_text(text)
        else:
            section:Section = self.section_search(header)
            section.add_text(text)

    def add_code(self, header:Optional[str]=None, code:str="\n") -> BaseSection:
        """
        Add a code section to the markdown file.

        Args:
            header (str): Header of the section.
            code (str): Code of the section.
        """
        if header is None:
            super().add_code(code)
        else:
            section:Section = self.section_search(header)
            section.add_code(code)

    def add_image(self, header:Optional[str]=None, fig:Union[Figure,str]="", caption:str="") -> BaseSection:
        """
        Add an image section to the markdown file.

        Args:
            header (str): Header of the section.
            fig (Figure): Figure to add to the section.
            caption (str): Caption of the section.
        """
        if header is None:
            super().add_image(fig, caption)
        else:
            section:Section = self.section_search(header)
            section.add_image(fig, caption)

    def add_list(self, header:Optional[str]=None, items:List[str]=[], marked_with:str="-") -> BaseSection:
        """
        Add a list section to the markdown file.

        Args:
            header (str): Header of the section.
            items (List[str]): Items of the section.
        """
        if header is None:
            super().add_list(items, marked_with)
        else:
            section:Section = self.section_search(header)
            section.add_list(items, marked_with)

    def add_link(self, header:Optional[str]=None, link:str="", text:str="") -> BaseSection:
        """
        Add a link section to the markdown file.

        Args:
            header (str): Header of the section.
            link (str): Link of the section.
            text (str): Text of the section.
        """
        if header is None:
            super().add_link(link, text)
        else:
            section:Section = self.section_search(header)
            section.add_link(link, text)

    def add_checkbox(self, header:Optional[str]=None, items:List[str]=[], checked:List[bool]=[]) -> BaseSection:
        """
        Add a checkbox section to the markdown file.

        Args:
            header (str): Header of the section.
            items (List[str]): Items of the section.
            checked (List[bool]): Checked status of the items.
        """
        if header is None:
            super().add_checkbox(items, checked)
        else:
            section:Section = self.section_search(header)
            section.add_checkbox(items, checked)

    def render(self) -> None:
        """
        Render the markdown file.
        """
        for section in self.values():
            section.render()
        self.mdFile.create_md_file()

    def is_valid(self) -> bool:
        """
        Check if the markdown file is valid.

        Returns:
            bool: True if the markdown file is valid, False otherwise.
        """
        for section in self.values():
            if not section.is_valid():
                return False
        return True
    
    def save(self, file_name:Optional[str] = None) -> None:
        """
        Save the markdown file.

        Args:
            file_name (Optional[str], optional): Name of the file to save. Defaults to None.
                - If None, the current file name is used.
        """
        if file_name is not None:
            if len(file_name.split("/")) > 1:
                self.save_path = Path("/".join(file_name.split("/")[:-1]))
                self.file_name = file_name.split("/")[-1]
            if file_name.split(".")[-1] == "md":
                self.file_name = ".".join(file_name.split(".")[:-1])

            self.mdFile.file_name = str(self.save_path / (self.file_name + ".md"))

        self.render()

    def _to_json(self) -> Dict:
        """
        Convert the markdown file to a normal dictionary.

        Returns:
            Dict: Dictionary representation of the markdown file.
        """
        json_dict = {}

        # Add settings
        json_dict["MDG_Settings"] = {
            "save_path": str(self.save_path),
            "file_name": self.file_name,
            "title": self.title,
            "author": self.author,
            "dpi": self.dpi,
            "section_headers": self.section_headers,
            "section_type_count": self.section_type_count
        }

        for key, value in self.items():
            json_dict[key] = value._to_json()
        return json_dict

    def save_json(self, file_name:Optional[str] = None) -> None:
        """
        Save the markdown file as a json file.

        Args:
            file_name (Optional[str], optional): Name of the json file. Defaults to None.
                - If None, the file is saved as "GeneratedMD.json".
        """
        if file_name is not None:
            if len(file_name.split("/")) > 1:
                save_path = Path("/".join(file_name.split("/")[:-1]))
                file_name = file_name.split("/")[-1]
            else:
                save_path = self.save_path

            if file_name.split(".")[-1] == "json":
                file_name = ".".join(file_name.split(".")[:-1])
        else:
            save_path = self.save_path
            file_name = self.file_name

        with open(str(save_path / (file_name + ".json")), "w") as f:
            json.dump(self._to_json(), f, indent=4)

    def load_json(self, file_name:Optional[str] = None) -> None:
        """
        Load a json file to create a markdown file.

        Args:
            file_name (Optional[str], optional): Name of the json file. Defaults to None.
                - If None, the file is loaded as "GeneratedMD.json".
        """
        if file_name is not None:
            if len(file_name.split("/")) > 1:
                save_path = Path("/".join(file_name.split("/")[:-1]))
                file_name = file_name.split("/")[-1]
            else:
                save_path = self.save_path

            if file_name.split(".")[-1] == "json":
                file_name = ".".join(file_name.split(".")[:-1])
        else:
            save_path = self.save_path
            file_name = self.file_name

        with open(str(save_path / (file_name + ".json")), "r") as f:
            json_dict = json.load(f)
        
        self.save_path = Path(json_dict["MDG_Settings"]["save_path"])
        self.file_name = json_dict["MDG_Settings"]["file_name"]
        self.title = json_dict["MDG_Settings"]["title"]
        self.author = json_dict["MDG_Settings"]["author"]
        self.dpi = json_dict["MDG_Settings"]["dpi"]
        self.section_headers = json_dict["MDG_Settings"]["section_headers"]
        self.section_type_count = SectionType.new_dictionary(SectionType)

        # Set the class variables for the Section class
        Section.save_path = self.save_path
        Section.dpi = self.dpi
        Section.section_headers = self.section_headers
        Section.section_type_count = self.section_type_count

        self.mdFile = MdUtils(file_name=str(self.save_path / (self.file_name + ".md")), title=self.title, author=self.author)
        for key, value in json_dict.items():
            if key != "MDG_Settings":
                if key in self.section_headers: # It is a Section Object
                    self[key]._from_json(value)
                else:       # It is not a Section Object
                    if isinstance(value, dict):
                        value_type = list(value.keys())[0]
                        if value_type == "text":
                            self.add_text(None, value["text"])
                        elif value_type == "code":
                            self.add_code(None, value["code"], value["language"])
                        elif value_type == "image":
                            self.add_image(None, value["image"], value["caption"])
                        elif value_type == "table":
                            self.add_table(None, value["table"], value["columns"], value["rows"])
                        elif value_type == "list":
                            self.add_list(None, value["list"])
                        elif value_type == "link":
                            self.add_link(None, value["link"], value["text"])
                        elif value_type == "checkbox":
                            self.add_checkbox(None, value["text_list"], value["checked"])
                    else:
                        raise ValueError(f"Value for key {key} is not a dictionary.")
        
        # Remove duplicate section headers
        i = 0
        while i < len(self.section_headers):
            if self.section_headers[i] in self.section_headers[:i]:
                self.section_headers.pop(i)
            else:
                i += 1



# if __name__ == "__main__":
#     # mdGen = MDGenerator()
#     # mdGen.load_json("example/GeneratedMD.json")
#     # mdGen.save()

#     mdGen = MDGenerator("example", title="Generated Markdown", author="Author")
#     mdGen.add_text("Section 1", "This is the first section.")
#     #mdGen["Section 1"].add_text("This is a subsection of the first section.")
#     # mdGen.add_text("Section 2", "This is the second section.")
#     mdGen["Section 2"].add_text("This is a subsection of the second section.")
#     # mdGen.add_code("Section 2", "print('Hello, World!')")
#     mdGen["Section 2"].add_code("print('This is a subsection of the second section.')")
#     # mdGen.add_text("Section 1/Subsection 1", "This is a subsection of the first section.")
#     mdGen["Section 1"]["Subsection 1"].add_text("This is a subsection of the first section.")
#     # mdGen.add_text("Section 1/Subsection 2", "This is a subsection of the first section.")
#     mdGen["Section 1"]["Subsection 2"].add_text("This is a subsection of the first section.")
#     mdGen["Section 1/Subsection 2"].add_text("Specifically, this is the second subsection of the first subsection.")

#     # mdGen.add_text("Section 1/Subsection 2/Subsubsection 1", "This is a subsubsection of the second subsection.")
#     mdGen["Section 1"]["Subsection 2"]["Subsubsection 1"].add_text("This is a subsubsection of the second subsection.")

#     mdGen["Section 1"] = "Hello"

#     import matplotlib.pyplot as plt
#     import numpy as np

#     # Generate random data
#     x = np.linspace(0, 10, 100)
#     y = np.random.randn(100)

#     # Create a figure and plot the data
#     fig, ax = plt.subplots()
#     ax.plot(x, y)

#     # Add labels and title
#     ax.set_xlabel('X-axis')
#     ax.set_ylabel('Y-axis')
#     ax.set_title('Random Figure')

#     # Add the image to the markdown file
#     # mdGen.add_image("Section 1", fig, "This is a random figure.")
#     mdGen["Section 1"].add_image(fig, "This is a random figure.")
#     mdGen["Section 1"].add_image(fig, "This is a random figure.")
#     mdGen["Section 1"].add_image(fig, "This is a random figure.")

#     # Add a list to the markdown file
#     # mdGen.add_list("Section 2", ["Item 1", "Item 2", "Item 3"])
#     mdGen["Section 2"].add_list(["Item 1", "Item 2", "Item 3"])

#     # Add a link to the markdown file
#     # mdGen.add_link("Section 2", "https://www.google.com", "Google")
#     mdGen["Section 2"].add_link("https://www.google.com", "Google")

#     # Add a checkbox list to the markdown file
#     # mdGen.add_checkbox("Section 2", ["Check 1", "Check 2", "Check 3"], [True, False, True])
#     mdGen["Section 2"].add_checkbox(["Check 1", "Check 2", "Check 3"], [True, False, True])

#     # Add a table to the markdown file
#     headers = ["Header 1", "Header 2", "Header 3", "Header 4"]
#     table = np.random.randint(0, 10, (6, 4))
#     df = DataFrame(table, columns=headers)

#     list_table = ["Header 1", "Header 2", "Header 3"] + [str(3*i + j) for i in range(3) for j in range(3)]
#     # mdGen.add_table("Section 3/Numpy Array Table", table)
#     mdGen["Section 3"]["Numpy Array Table"].add_table(table)
#     # mdGen.add_table("Section 3/Python List Table", list_table, 3, 4)
#     mdGen["Section 3"]["Python List Table"].add_table(list_table, 3, 4)
#     # mdGen.add_table("Section 3/Pandas DataFrame Table", df)
#     mdGen["Section 3"]["Pandas DataFrame Table"].add_table(df)

#     # Save the markdown file
#     mdGen.save_json()
#     mdGen.save()