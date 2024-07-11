from abc import ABC, abstractmethod
from typing import List, Optional, Union
from mdutils.mdutils import MdUtils


class BaseSection(ABC):
    """
    Abstract class for a section in the markdown report. All types of sections must inherit from this class.
    """
    sections = {}

    def __init__(self, md_file: MdUtils, location:str):
        self.md_file = md_file
        self.location = location

    @abstractmethod
    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        """
        Render the section in the markdown file. This section should include all the pre-processing required to render
        followed by a call to some MdUtils methods to render the section.

        Example MdUtils methods: new_header, new_paragraph, new_inline_image, insert_code, etc.
        """

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Is the section valid to be rendered in the markdown file. If this returns False, the section will be ignored
        during rendering.
        """

class Section(BaseSection):
    """
    Section to hold multiple sections in the markdown file.
    """
    sections:dict = {}
    text:int = 0
    code:int = 0
    image:int = 0
    table:int = 0
    list:int = 0
    link:int = 0
    checkbox:int = 0
    
    def __init__(self, md_file: MdUtils, header:str, location:str):
        super().__init__(md_file, location)
        self.header = header

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.new_header(level=level, title=self.header)
        if space_below:
            self.md_file.new_line()

        level += 1
        for section in self.sections:
            section.render(level=level)
    
    def is_valid(self) -> bool:
        for section in self.sections:
            if not section.is_valid():
                return False
        return True
    
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
        # elif isinstance(section, TableSection):
        #     name = f"table{self.table}"
        #     self.table += 1
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
        
    
    def add_section(self, heading:str, location:str, section:Optional[BaseSection] = None, section_headers:List[str] = []) -> bool:
        """
        Create a new section in the markdown file.

        Args:
            heading (str): Heading of the section.
            section (Optional[BaseSection], optional): Section to add to the markdown file. Defaults to None.
                - If None, a new Section object is created.

        Returns:
            bool: True if the section was added successfully, False if the section already exists.
        """
        headers = heading.split("/") # Split the heading into subheadings
        header = headers[0]
        new_location = location + '/' + header
        result = False

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if header not in self.sections.keys():  # If the section does not exist, create it
                if section is None:
                    self.sections[header] = Section(self.mdFile, header, new_location)
                    section_headers.append(new_location)
                else:
                    self.sections[self.get_section_name(section)] = section
                result = True
            else:
                return result    # Section already exists
        else:
            if header not in self.sections.keys():  # If the section does not exist, create it
                self.sections[header] = Section(self.mdFile, header, new_location)
                section_headers.append(new_location)
            result = self.sections[header].add_section("/".join(headers[1:]), new_location, section, section_headers)   # Recursively add the section to the next level
        
        return result

class TextSection(BaseSection):
    """
    Section to render text in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, text:str):
        super().__init__(md_file, location)
        self.text = text

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.new_paragraph(text=self.text)
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        return True


class CodeSection(BaseSection):
    """
    Section to render code in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, code:str, language:str=""):
        super().__init__(md_file, location)
        self.code = code
        self.language = language

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.insert_code(code=self.code, language=self.language)
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        if len(self.code) == 0:
            return False
        return True
    

class ImageSection(BaseSection):
    """
    Section to render an image in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, image_path:str, caption:str=None):
        super().__init__(md_file, location)
        self.image_path = image_path
        self.caption = caption

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.new_inline_image(text=self.caption, path=self.image_path)
        #self.md_file.new_line(text=rf"![{self.heading}]({self.image_path})")
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        return True
    

# class TableSection(BaseSection):
#     """
#     Section to render a table in the markdown file.
#     """
#     def __init__(self, md_file: MdUtils, location:str, table:dict):
#         super().__init__(md_file, location)
#         self.table = table

#     def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
#         if space_above:
#           self.md_file.new_line()
#         self.md_file.new_table(columns=3, rows=3, text=self.table)
#         if space_below:
#           self.md_file.new_line()

#     def is_valid(self) -> bool:
#         return True

class ListSection(BaseSection):
    """
    Section to render a list in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, items:list):
        super().__init__(md_file, location)
        self.items = items

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.new_list(items=self.items)
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        return True
    
class LinkSection(BaseSection):
    """
    Section to render a link in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, link:str, text:str):
        super().__init__(md_file, location)
        self.link = link
        self.text = text

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        self.md_file.new_line(text=rf"[{self.text}]({self.link})")
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        return True
    
class CheckBoxSection(BaseSection):
    """
    Section to render a checkbox in the markdown file.
    """
    def __init__(self, md_file: MdUtils, location:str, text_list:List[str], checked:Union[List[bool],bool]=False):
        super().__init__(md_file, location)
        self.text_list = text_list
        if isinstance(checked, bool):
            self.checked = [checked for _ in range(len(text_list))]
        elif isinstance(checked, list) and (len(checked) == len(text_list)):
            self.checked = checked
        else:
            raise ValueError("checked must be a boolean or a list of booleans with the same length as text.")

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.md_file.new_line()
        for text, checked in zip(self.text_list, self.checked):
            self.md_file.new_line(text=rf"- [x]" if checked else rf"- [ ]" + f" {text}")
        if space_below:
            self.md_file.new_line()

    def is_valid(self) -> bool:
        return True