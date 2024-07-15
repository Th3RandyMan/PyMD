from abc import ABC, abstractmethod
from collections import UserDict
from pathlib import Path
from typing import Dict, List, Optional, Union
from matplotlib.figure import Figure
from mdutils.mdutils import MdUtils
import numpy as np
from pandas import DataFrame
from .utils import FIGURE_FOLDER

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

class Section(BaseSection, UserDict):
    """
    Section to hold multiple sections in the markdown file.
    """
    save_path:Path = None
    dpi:int = None

    def __init__(self, mdFile: MdUtils, header:str, location:str="", section_headers:Optional[List[str]]=None):
        UserDict.__init__(self)
        BaseSection.__init__(self, mdFile, location)
        self.header = header
        self.section_headers = section_headers
        if section_headers is not None:
            self.section_headers.append(self.get_header_location())
        # self:dict = {}
        self.text:int = 0
        self.code:int = 0
        self.image:int = 0
        self.table:int = 0
        self.list:int = 0
        self.link:int = 0
        self.checkbox:int = 0

    # def __getstate__(self) -> Dict:
    #     return self.__dict__
    
    def _from_json(self, json_dict:Dict) -> None:
        """
        Convert a dictionary to a markdown file.

        Args:
            json_dict (Dict): Dictionary representation of the markdown file.
        """
        location = self.get_header_location()
        relative_headers = [x.replace(location + "/", "") for x in self.section_headers if x.startswith(location + "/")]

        for key, value in json_dict.items():
            if key in relative_headers:
                self[key]._from_json(value)
            else:
                if isinstance(value, dict):
                    value_type = list(value.keys())[0]
                    if value_type == "text":
                        self.add_text(value["text"])
                    elif value_type == "code":
                        self.add_code(value["code"], value["language"])
                    elif value_type == "image":
                        self.add_image(value["image"], value["caption"])
                    elif value_type == "table":
                        self.add_table(value["table"], value["columns"], value["rows"])
                    elif value_type == "list":
                        self.add_list(value["list"])
                    elif value_type == "link":
                        self.add_link(value["link"], value["text"])
                    elif value_type == "checkbox":
                        self.add_checkbox("", value["text_list"], value["checked"])
                else:
                    raise ValueError(f"Value for key {key} is not a dictionary.")

    
    def _to_json(self) -> Dict:
        """
        Convert the markdown file to a normal dictionary.

        Returns:
            Dict: Dictionary representation of the markdown file.
        """
        json_dict = {}
        for key, value in self.items():
            json_dict[key] = value._to_json()
        return json_dict

    def get_section_ptr(self, keys:List[str]) -> BaseSection:
        ptr = self
        for k in keys[:-1]:
            ptr = ptr[k]
        return ptr, keys[-1]

    def __setitem__(self, key:str, section:BaseSection):
        if section is not None and isinstance(section, Section) and section.section_headers is None:
            self.section_headers.append(self.get_header_location())

        if key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__setitem__(new_key, section)
        else:
            return super().__setitem__(key, section)
    
    def __getitem__(self, key:str) -> BaseSection:
        if key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__getitem__(new_key)
        else:
            if key not in self:
                self[key] = Section(self.mdFile, key, self.get_header_location(), self.section_headers)
            return super().__getitem__(key)
    
    def __delitem__(self, key: str) -> None:     # Need to make this delete all strings with key in it
        if self.section_headers is not None and key in self.section_headers:
            self.section_headers.remove(key)
        return super().__delitem__(key)
    ### FIX THIS -> MAYBE ADD IN self.get_header_location() instead of key? Or self.get_header_location() + key

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_header(level=level, title=self.header)
        if space_below:
            self.mdFile.new_line()

        level += 1
        for section_name, section in self.items():
            section.render(level=level)
    
    def is_valid(self) -> bool:
        for section_name, section in self:
            if not section.is_valid():
                return False
        return True
    
    def get_header_location(self) -> str:
        """
        Get the heading of the section.

        Returns:
            str: Heading of the section.
        """
        return self.header if self.location == '' else self.location + '/' + self.header

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
            bool: True if the section was added successfully, False if the section already exists.
        """
        if heading is None: # If the heading is None, add the section to the current section
            if section is None:
                return section
            else:
                self[self.get_section_name(section)] = section
                return section

        headers = heading.split("/") # Split the heading into subheadings
        head = headers[0]

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, self.get_header_location(), self.section_headers)

                if section is not None:
                    section = self[head].add_section(None, section)
                else:
                    section = self[head]
            elif section is not None:
                section = self[head].add_section(None, section)
        elif len(headers) > 1:
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, self.get_header_location(), self.section_headers)

            section = self[head].add_section("/".join(headers[1:]), section)   # Recursively add the section to the next level
        
        return section
    
    def add_text(self, text:str) -> BaseSection:
        """
        Add a text section to the markdown file.

        Args:
            text (str): Text to add to the markdown file.

        Returns:
            BaseSection: Text section object.
        """
        return self.add_section(None, TextSection(self.mdFile, self.get_header_location(), text))
    
    def add_code(self, code:str, language:str="python") -> BaseSection:
        """
        Add a code section to the markdown file.

        Args:
            code (str): Code to add to the markdown file.
            language (str, optional): Language of the code. Defaults to "python".

        Returns:
            BaseSection: Code section object.
        """
        return self.add_section(None, CodeSection(self.mdFile, self.get_header_location(), code, language))
    
    def add_image(self, figure:Union[Figure,str], caption:str=None) -> BaseSection:
        """
        Add an image section to the markdown file.

        Args:
            image_path (str): Path to the image file.
            caption (str, optional): Caption for the image. Defaults to None.

        Returns:
            BaseSection: Image section object.
        """
        if isinstance(figure, Figure):
            # Save the figure
            image_path = self.save_path / FIGURE_FOLDER
            if not image_path.exists():
                image_path.mkdir()
            image_path = image_path / f"image{self.image}.png"
            figure.savefig(str(image_path), dpi=self.dpi)
            figure = str(image_path)

        return self.add_section(None, ImageSection(self.mdFile, self.get_header_location(), figure, caption))
    
    def add_table(self, table:List[str], columns:int=3, rows:int=3) -> BaseSection:
        """
        Add a table section to the markdown file.

        Args:
            table (List[str]): Table data.
            columns (int, optional): Number of columns in the table. Defaults to 3.
            rows (int, optional): Number of rows in the table. Defaults to 3.

        Returns:
            BaseSection: Table section object.
        """
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

        return self.add_section(None, TableSection(self.mdFile, self.get_header_location(), table, columns, rows))
    
    def add_list(self, items:list) -> BaseSection:
        """
        Add a list section to the markdown file.

        Args:
            items (list): List of items.

        Returns:
            BaseSection: List section object.
        """
        return self.add_section(None, ListSection(self.mdFile, self.get_header_location(), items))
    
    def add_link(self, link:str, text:str) -> BaseSection:
        """
        Add a link section to the markdown file.

        Args:
            link (str): Link to add.
            text (str): Text to display for the link.

        Returns:
            BaseSection: Link section object.
        """
        return self.add_section(None, LinkSection(self.mdFile, self.get_header_location(), link, text))
    
    def add_checkbox(self, text_list:List[str], checked:Union[List[bool],bool]=False) -> BaseSection:
        """
        Add a checkbox section to the markdown file.

        Args:
            text_list (List[str]): List of text items.
            checked (Union[List[bool],bool], optional): List of booleans indicating if the checkbox is checked. Defaults to False.

        Returns:
            BaseSection: Checkbox section object.
        """
        return self.add_section(None, CheckBoxSection(self.mdFile, self.get_header_location(), text_list, checked))
    

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
    
    def _to_json(self) -> Dict:
        return {
            "text": self.text
        }


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
    
    def _to_json(self) -> Dict:
        return {
            "code": self.code,
            "language": self.language
        }
    

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
    
    def _to_json(self) -> Dict:
        return {
            "image_path": str(self.image_path),
            "caption": self.caption
        }
    

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
    
    def _to_json(self) -> Dict:
        return {
            "table": self.table,
            "columns": self.columns,
            "rows": self.rows
        }

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
    
    def _to_json(self) -> Dict:
        return {
            "items": self.items
        }
    
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
    
    def _to_json(self) -> Dict:
        return {
            "link": self.link,
            "text": self.text
        }
    
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
    
    def _to_json(self) -> Dict:
        return {
            "text_list": self.text_list,
            "checked": self.checked
        }