"""
Generate a markdown file with images and text.
To do:
    - Add author write in and list object for multiple
    - Maybe add in deconstructor to save the file?
    - Increment count variables for index assignment (text, code, image, table, list, link, checkbox in Section class).
    - Have not tested section_headers deletion, and there could be issues with some adding methods.
    - Fix location for base since location is currently None and "".
"""
from collections import UserDict
import json
from matplotlib.figure import Figure
from mdutils.mdutils import MdUtils
from pathlib import Path
from typing import Dict, Optional, Union, List

from pandas import DataFrame
import numpy as np
from .tools.utils import is_file_type, FIGURE_FOLDER
from .tools.sections import *



class MDGenerator(UserDict):
    """
    Class to generate a markdown file with images and text.
    """
    # text_count = 0
    # code_count = 0
    # image_count = 0
    # table_count = 0
    # list_count = 0
    # link_count = 0
    # checkbox_count = 0

    def __init__(self, save_path: Optional[Union[str,Path]] = None, file_name:str = "GeneratedMD", title:Optional[str] = None, author:Optional[str] = None, dpi:Optional[int] = None):
        """
        Args:
            save_path (Optional[Union[str,Path]], optional): Path to save the generated file. Defaults to None.
                - If None, the current working directory is used.
            file_name (str, optional): Name of the generated file. Defaults to "GeneratedMD".
            title (str, optional): Title of the document. Defaults to None.
            author (str, optional): Author of the document. Defaults to None.
            dpi (int, optional): DPI of the generated image. Defaults to None, figures dpi.
        """
        super().__init__()

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
        Section.save_path = self.save_path

        self.file_name = file_name
        if title is None:
            self.title = ""
        else:
            self.title = title
        if author is None:
            self.author = ""
        else:
            self.author = author
        
        self.dpi = dpi
        Section.dpi = self.dpi
        
        self.mdFile = MdUtils(file_name=str(self.save_path / (file_name + ".md")), title=self.title, author=self.author)
        self.section_headers:List[str] = []

        self.text = 0
        self.code = 0
        self.image = 0
        self.table = 0
        self.list = 0
        self.link = 0
        self.checkbox = 0

    # def __getstate__(self) -> Dict:
    #     return self.__dict__
    
    # def __setstate__(self, state:Dict) -> None:
    #     self.__dict__.update(state)

    def get_section_ptr(self, keys:List[str]) -> BaseSection:
        ptr = self
        for k in keys[:-1]:
            ptr = ptr[k]
        return ptr, keys[-1]

    def __setitem__(self, key:str, section:Union[BaseSection, str, DataFrame, np.ndarray, Figure]) -> None:
        if section is not None and isinstance(section, Section) and section.section_headers is None:
            self.section_headers.append(key)

        if key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__setitem__(new_key, section)
        else:
            if isinstance(section, BaseSection):
                return super().__setitem__(key, section)
            elif isinstance(section, str):
                self.add_text(None, section)
            elif isinstance(section, DataFrame):
                self.add_table(None, section)
            elif isinstance(section, np.ndarray):
                self.add_table(None, section)
            elif isinstance(section, Figure):
                self.add_image(None, section)
            else:
                raise ValueError("Invalid section type.")
    
    def __getitem__(self, key:str) -> BaseSection:
        if key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__getitem__(new_key)
        else:
            if key not in self:
                self[key] = Section(self.mdFile, key, "", self.section_headers)
            return super().__getitem__(key)
    
    def __delitem__(self, key:str) -> None:
        if key in self.section_headers:     # Need to make this delete all strings with key in it
            self.section_headers.remove(key)
        return super().__delitem__(key)
    
    def get_section_name(self, section:BaseSection) -> str:
        """
        Get the name of the section based on the type of section.

        Args:
            section (BaseSection): Section object to get the name of.

        Returns:
            str: Name of the section.
        """
        if isinstance(section, Section):
            name = section.header
        elif isinstance(section, TextSection):
            name = f"text{self.text}"
            self.text += 1
        elif isinstance(section, CodeSection):
            name = f"code{self.code}"
            self.code += 1
        elif isinstance(section, ImageSection):
            name = f"image{self.image}"
            self.image += 1
        elif isinstance(section, TableSection):
            name = f"table{self.table}"
            self.table += 1
        elif isinstance(section, ListSection):
            name = f"list{self.list}"
            self.list += 1
        elif isinstance(section, LinkSection):
            name = f"link{self.link}"
            self.link += 1
        elif isinstance(section, CheckBoxSection):
            name = f"checkbox{self.checkbox}"
            self.checkbox += 1
        else:
            raise ValueError("Invalid section type.")
        
        return name

    def add_section(self, heading:Optional[str], section:Optional[BaseSection] = None) -> BaseSection:
        """
        Create a new section in the markdown file.

        Args:
            heading (str): Heading of the section.
            section (Optional[BaseSection], optional): Section to add to the markdown file. Defaults to None.
                - If None, a new Section object is created.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        type_section = False
        if isinstance(section, Section):
            type_section = True

        if heading is None:
            if section is None:
                return section
            else:
                self[self.get_section_name(section)] = section
                return section

        elif heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        headers = heading.split("/") # Split the heading into subheadings
        head = headers[0]

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, "", self.section_headers)
                # self.section_headers.append(head)
                if section is not None:
                    section = self[head].add_section(None, section)
                else:
                    section = self[head]
            elif section is not None:
                section = self[head].add_section(None, section)
        elif len(headers) > 1:
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, "", self.section_headers)
                # self.section_headers.append(head)

            section = self[head].add_section("/".join(headers[1:]), section)   # Recursively add the section to the next level
        
        if type_section and section is not None:    # If given object is a Section object, missed adding the section to the section list
            self.section_headers.append(heading)

        return section

        
    def add_text(self, heading:str, text:str) -> BaseSection:
        """
        Add text to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            text (str): Text to add to the section.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]

        section = TextSection(self.mdFile, heading, text)
        result = self.add_section(heading, section)
        if result:
            self.text += 1
        return result

    def add_image(self, heading:str, figure:Union[Figure,str], caption:str = None) -> BaseSection:
        """
        Add an image to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            figure (Union[Figure,str]): Figure object or path to the image.
                - If a path is given, give relative path, not absolute path.
            caption (str, optional): Caption for the image. Defaults to None.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]

        if isinstance(figure, Figure):
            # Save the figure
            image_path = self.save_path / FIGURE_FOLDER
            if not image_path.exists():
                image_path.mkdir()
            image_path = image_path / f"image{self.image}.png"
            figure.savefig(str(image_path), dpi=self.dpi)

        section = ImageSection(self.mdFile, heading, image_path, caption)
        result = self.add_section(heading, section)
        if result:
            self.image += 1
        return result
    
    def add_code(self, heading:str, code:str, language:str = "python") -> BaseSection:
        """
        Add code to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            code (str): Code to add to the section.
            language (str, optional): Language of the code. Defaults to "python".

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        section = CodeSection(self.mdFile, heading, code, language)
        result = self.add_section(heading, section)

        if result:
            self.code += 1
        return result
    
    def add_table(self, heading:str, table:Union[DataFrame, np.ndarray, List[str]], columns:int=None, rows:int=None) -> BaseSection:
        """
        Add a table to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            table (List[List[str]]): Table to add to the section.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]

        if isinstance(table, DataFrame):
            rows, columns = table.shape
            col = table.columns.tolist()
            rows += 1
            table = col + [str(x) for x in table.values.flatten().tolist()]
        elif isinstance(table, np.ndarray):
            rows, columns = table.shape
            col = [f"Column {x+1}" for x in range(table.shape[1])]
            rows += 1
            table = col + [str(x) for x in table.flatten().tolist()]
        elif table is None:
            raise ValueError("Table cannot be None.")
            
        # Check if table size is valid
        if columns is not None and rows is not None:
            if columns * rows != len(table):
                raise ValueError("Table size does not match the number of rows and columns.")
        else:
            raise ValueError("Number of columns and rows must be specified.")
            
        section = TableSection(self.mdFile, heading, table, columns, rows)
        result = self.add_section(heading, section)

        if result:
            self.table += 1
        return result

    def add_list(self, heading:str, items:List[str]) -> BaseSection:
        """
        Add a list to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            items (List[str]): Items to add to the list.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        section = ListSection(self.mdFile, heading, items)
        result = self.add_section(heading, section)

        if result:
            self.list += 1
        return result
    
    def add_link(self, heading:str, link:str, text:str) -> BaseSection:
        """
        Add a link to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            link (str): Link to add to the section.
            text (str): Text to display for the link.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        section = LinkSection(self.mdFile, heading, link, text)
        result = self.add_section(heading, section)

        if result:
            self.link += 1
        return result
    
    def add_checkbox(self, heading:str, text_list:List[str], checked:Union[List[bool],bool] = False) -> BaseSection:
        """
        Add a checkbox list to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            text_list (List[str]): List of text items for the checkbox list.
            checked (Union[List[bool],bool], optional): List of booleans to check each checkbox. Defaults to False.

        Returns:
            BaseSection: Section object that was added to the markdown file.
        """
        if heading is not None and heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        section = CheckBoxSection(self.mdFile, heading, text_list, checked)
        result = self.add_section(heading, section)

        if result:
            self.checkbox += 1
        return result
    
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
            # "text_count": self.text,
            # "code_count": self.code,
            # "image_count": self.image,
            # "table_count": self.table,
            # "list_count": self.list,
            # "link_count": self.link,
            # "checkbox_count": self.checkbox
        }

        for key, value in self.items():
            json_dict[key] = value._to_json()
        return json_dict
    
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
        # self.text = json_dict["MDG_Settings"]["text_count"]
        # self.code = json_dict["MDG_Settings"]["code_count"]
        # self.image = json_dict["MDG_Settings"]["image_count"]
        # self.table = json_dict["MDG_Settings"]["table_count"]
        # self.list = json_dict["MDG_Settings"]["list_count"]
        # self.link = json_dict["MDG_Settings"]["link_count"]
        # self.checkbox = json_dict["MDG_Settings"]["checkbox_count"]

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
    
    def save(self, file_name:Optional[str] = None) -> None:
        """
        Save the markdown file.

        """
        if file_name is not None:
            if len(file_name.split("/")) > 1:
                self.save_path = Path("/".join(file_name.split("/")[:-1]))
                self.file_name = file_name.split("/")[-1]
            if file_name.split(".")[-1] == "md":
                self.file_name = ".".join(file_name.split(".")[:-1])

            self.mdFile.file_name = str(self.save_path / (self.file_name + ".md"))

        for section in self.values():
            section.render()
        self.mdFile.create_md_file()
    

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