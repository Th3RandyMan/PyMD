from abc import ABC, abstractmethod
from typing import List, Optional, Union
from mdutils.mdutils import MdUtils


class BaseSection(ABC):
    """
    Abstract class for a section in the markdown report. All types of sections must inherit from this class.
    """
    def __init__(self, mdFile: MdUtils, location:str):
        self.mdFile = mdFile
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
    def __init__(self, mdFile: MdUtils, header:str, location:str):
        super().__init__(mdFile, location)
        self.header = header
        self.sections:dict = {}
        self.text:int = 0
        self.code:int = 0
        self.image:int = 0
        self.table:int = 0
        self.list:int = 0
        self.link:int = 0
        self.checkbox:int = 0

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_header(level=level, title=self.header)
        if space_below:
            self.mdFile.new_line()

        level += 1
        for section_name, section in self.sections.items():
            section.render(level=level)
    
    def is_valid(self) -> bool:
        for section_name, section in self.sections:
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
        
    
    def add_section(self, heading:Optional[str], section:Optional[BaseSection] = None, section_headers:Optional[List[str]] = None) -> BaseSection:
        """
        Create a new section in the markdown file.

        Args:
            heading (str): Heading of the section.
            section (Optional[BaseSection], optional): Section to add to the markdown file. Defaults to None.
                - If None, a new Section object is created.
            section_headers (Optional[List[str]], optional): List to store the headers of the sections. Defaults to None.

        Returns:
            bool: True if the section was added successfully, False if the section already exists.
        """
        if heading is None: # If the heading is None, add the section to the current section
            if section is None:
                return section
            else:
                self.sections[self.get_section_name(section)] = section
                return section

        headers = heading.split("/") # Split the heading into subheadings
        head = headers[0]
        location = self.header if self.location == '' else self.location + '/' + self.header

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if head not in self.sections.keys():  # If the section does not exist, create it
                self.sections[head] = Section(self.mdFile, head, location)
                if section_headers is not None:
                    section_headers.append(head)

                if section is not None:
                    section = self.sections[head].add_section(None, section)
                else:
                    section = self.sections[head]
            elif section is not None:
                section = self.sections[head].add_section(None, section)
        elif len(headers) > 1:
            if head not in self.sections.keys():  # If the section does not exist, create it
                self.sections[head] = Section(self.mdFile, head, "")
                if section_headers is not None:
                    section_headers.append(head)

            section = self.sections[head].add_section("/".join(headers[1:]), section, section_headers)   # Recursively add the section to the next level
        
        return section
    

class TextSection(BaseSection):
    """
    Section to render text in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, text:str):
        super().__init__(mdFile, location)
        self.text = text

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_paragraph(text=self.text)
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True


class CodeSection(BaseSection):
    """
    Section to render code in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, code:str, language:str=""):
        super().__init__(mdFile, location)
        self.code = code
        self.language = language

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.insert_code(code=self.code, language=self.language)
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        if len(self.code) == 0:
            return False
        return True
    

class ImageSection(BaseSection):
    """
    Section to render an image in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, image_path:str, caption:str=None):
        super().__init__(mdFile, location)
        self.image_path = image_path
        self.caption = caption

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_line(self.mdFile.new_inline_image(text=self.caption, path=str(self.image_path)))
        #self.mdFile.new_line(text=rf"![{self.caption}]({str(self.image_path)})")
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True
    

class TableSection(BaseSection):
    """
    Section to render a table in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, table:List[str], columns:int=3, rows:int=3):
        super().__init__(mdFile, location)
        self.table = table
        self.columns = columns
        self.rows = rows

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
          self.mdFile.new_line()
        self.mdFile.new_table(columns=self.columns, rows=self.rows, text=self.table)
        if space_below:
          self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True

class ListSection(BaseSection):
    """
    Section to render a list in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, items:list):
        super().__init__(mdFile, location)
        self.items = items

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_list(items=self.items)
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True
    
class LinkSection(BaseSection):
    """
    Section to render a link in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, link:str, text:str):
        super().__init__(mdFile, location)
        self.link = link
        self.text = text

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_line(text=rf"[{self.text}]({self.link})")
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True
    
class CheckBoxSection(BaseSection):
    """
    Section to render a checkbox in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, text_list:List[str], checked:Union[List[bool],bool]=False):
        super().__init__(mdFile, location)
        self.text_list = text_list
        if isinstance(checked, bool):
            self.checked = [checked for _ in range(len(text_list))]
        elif isinstance(checked, list) and (len(checked) == len(text_list)):
            self.checked = checked
        else:
            raise ValueError("checked must be a boolean or a list of booleans with the same length as text.")

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        for text, checked in zip(self.text_list, self.checked):
            self.mdFile.new_line(text=rf"- [x]" + f" {text}" if checked else rf"- [ ]" + f" {text}")
        if space_below:
            self.mdFile.new_line()

    def is_valid(self) -> bool:
        return True