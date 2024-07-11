"""
Generate a markdown file with images and text.
To do:
    - Change section format to hold multiple sections.
    - Add a method to save the file.
"""
from matplotlib.figure import Figure
from mdutils.mdutils import MdUtils
from pathlib import Path
from typing import Dict, Optional, Union
from tools.utils import is_file_type
from tools.sections import *


# def process_heading(heading:str) -> str:
#     """
#     Process the heading to remove any empty headers and return the final heading.

#     Args:
#         heading (str): Heading to process.

#     Returns:
#         str: Processed heading.
#     """
#     headers = heading.split("/") # Split the heading into subheadings
#     for i in range(1, len(headers)):    # Remove any empty headers except the first one
#         if headers[i] == "":
#             headers.pop(i)
#     return "/".join(headers)

class MDGenerator:
    """

    """
    text:int = 0
    code:int = 0
    image:int = 0
    table:int = 0
    list:int = 0
    link:int = 0
    checkbox:int = 0

    FIGURE_FOLDER = "figures"

    def __init__(self, save_path: Optional[Union[str,Path]] = None, file_name:str = "GeneratedMD", title:str = None, author:str = None, dpi:int = 300):
        """
        Args:
            save_path (Optional[Union[str,Path]], optional): Path to save the generated file. Defaults to None.
                - If None, the current working directory is used.
            file_name (str, optional): Name of the generated file. Defaults to "GeneratedMD".
            title (str, optional): Title of the document. Defaults to None.
            author (str, optional): Author of the document. Defaults to None.
            dpi (int, optional): DPI of the generated image. Defaults to 300.
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
        self.title = title
        self.author = author
        self.dpi = dpi
        
        self.mdFile = MdUtils(file_name=str(self.save_path) + file_name + ".md", title=title, author=author)
        self.sections:Dict[Section] = {}
        self.section_headers:List[str] = []

    def add_section(self, heading:Optional[str], section:Optional[BaseSection] = None) -> bool:
        """
        Create a new section in the markdown file.

        Args:
            heading (str): Heading of the section.
            section (Optional[BaseSection], optional): Section to add to the markdown file. Defaults to None.
                - If None, a new Section object is created.

        Returns:
            bool: True if the section was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        headers = heading.split("/") # Split the heading into subheadings
        head = headers[0]
        result = False

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if head not in self.sections.keys():  # If the section does not exist, create it
                if section is None:
                    self.sections[head] = Section(self.mdFile, head, "")
                    self.section_headers.append(head)
                else:
                    self.sections[head] = section
                result = True
            else:
                return result    # Section already exists
        elif len(headers) > 1:
            if head not in self.sections.keys():  # If the section does not exist, create it
                self.sections[head] = Section(self.mdFile, head, "")
                self.section_headers.append(head)
            result = self.sections[head].add_section("/".join(headers[1:]), head, section, self.section_headers)   # Recursively add the section to the next level
        
        return result

        
    def add_text(self, heading:str, text:str) -> bool:
        """
        Add text to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            text (str): Text to add to the section.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]

        section = TextSection(self.mdFile, heading, text)
        result = self.add_section(heading, section)
        if result:
            self.text += 1
        return result

    def add_image(self, heading:str, figure:Union[Figure,str], caption:str = None) -> bool:
        """
        Add an image to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            figure (Union[Figure,str]): Figure object or path to the image.
            caption (str, optional): Caption for the image. Defaults to None.

        Returns:
            bool: True if the image was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/": # Remove the first slash if it exists
            heading = heading[1:]
        result = False

        if isinstance(figure, Figure):
            # Save the figure
            image_path = self.save_path / MDGenerator.FIGURE_FOLDER #str(self.save_path) + "/" + f"image{self.image}.png"
            if not image_path.exists():
                image_path.mkdir()
            image_path = image_path / f"image{self.image}.png"
            figure.savefig(str(image_path), dpi=self.dpi)

        section = ImageSection(self.mdFile, heading, image_path, caption)
        result = self.add_section(heading, section)
        if result:
            self.image += 1
        return result
    
    def add_code(self, heading:str, code:str, language:str = "python") -> bool:
        """
        Add code to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            code (str): Code to add to the section.
            language (str, optional): Language of the code. Defaults to "python".

        Returns:
            bool: True if the code was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/":
            heading = heading[1:]
        section = CodeSection(self.mdFile, heading, code, language)
        result = self.add_section(heading, section)

        if result:
            self.code += 1
        return result
    
    # def add_table(self, heading:str, table:List[List[str]]) -> bool:
    #     """
    #     Add a table to a section in the markdown file.

    #     Args:
    #         heading (str): Heading of the section.
    #         table (List[List[str]]): Table to add to the section.

    #     Returns:
    #         bool: True if the table was added successfully, False if the section already exists.
    #     """
    #     if heading is None:
    #         heading = ""
    #     elif heading[0] == "/":
    #         heading = heading[1:]
    #     section = TableSection(self.mdFile, heading, table)
    #     result = self.add_section(heading, section)

    #     if result:
    #         self.table += 1
    #     return result

    def add_list(self, heading:str, items:List[str]) -> bool:
        """
        Add a list to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            items (List[str]): Items to add to the list.

        Returns:
            bool: True if the list was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/":
            heading = heading[1:]
        section = ListSection(self.mdFile, heading, items)
        result = self.add_section(heading, section)

        if result:
            self.list += 1
        return result
    
    def add_link(self, heading:str, link:str, text:str) -> bool:
        """
        Add a link to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            link (str): Link to add to the section.
            text (str): Text to display for the link.

        Returns:
            bool: True if the link was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/":
            heading = heading[1:]
        section = LinkSection(self.mdFile, heading, link, text)
        result = self.add_section(heading, section)

        if result:
            self.link += 1
        return result
    
    def add_checkbox(self, heading:str, text_list:List[str], checked:Union[List[bool],bool] = False) -> bool:
        """
        Add a checkbox list to a section in the markdown file.

        Args:
            heading (str): Heading of the section.
            text_list (List[str]): List of text items for the checkbox list.
            checked (Union[List[bool],bool], optional): List of booleans to check each checkbox. Defaults to False.

        Returns:
            bool: True if the checkbox list was added successfully, False if the section already exists.
        """
        if heading is None:
            heading = ""
        elif heading[0] == "/":
            heading = heading[1:]
        section = CheckBoxSection(self.mdFile, heading, text_list, checked)
        result = self.add_section(heading, section)

        if result:
            self.checkbox += 1
        return result
    
    def save(self):
        """
        Save the markdown file.
        """
        for section in self.sections.values():
            section.render()
        self.mdFile.create_md_file()
    

if __name__ == "__main__":
    mdGen = MDGenerator()
    mdGen.add_text("Section 1", "This is the first section.")
    mdGen.add_text("Section 2", "This is the second section.")
    #mdGen.add_image("Section 3", "image.png", "This is an image.")
    mdGen.mdFile.create_md_file()