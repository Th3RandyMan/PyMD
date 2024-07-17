from abc import ABC, abstractmethod
from collections import UserDict
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, Optional, Union
from matplotlib.figure import Figure
from mdutils.mdutils import MdUtils
import numpy as np
from pandas import DataFrame
from .utils import FIGURE_FOLDER


class SectionType(IntEnum):
    """
    Enum to define the type of section.
    """
    TEXT = 0
    CODE = 1
    IMAGE = 2
    TABLE = 3
    LIST = 4
    LINK = 5
    CHECKBOX = 6

    def new_dictionary(self) -> Dict:
        return {self.TEXT: 0, self.CODE: 0, self.IMAGE: 0, self.TABLE: 0, self.LIST: 0, self.LINK: 0, self.CHECKBOX: 0}

    def __str__(self):
        return self.name.lower()


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
    section_headers:List[str] = None
    section_type_count:Dict[SectionType,int] = None

    def __init__(self, mdFile: MdUtils, header:Optional[str] = None, location:Optional[str] = None):
        """
        Section to hold multiple sections in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the sections.
            header (Optional[str], optional): Heading of the section. Defaults to None.
            location (Optional[str], optional): Location of the section. Defaults to None.
        """
        UserDict.__init__(self)
        BaseSection.__init__(self, mdFile, location)
        self.header = header
        if header is not None:
            self.section_headers.append(self.get_header_location())
        self.base_name = mdFile.file_name.split("/")[-1].split(".")[0]

        self.text:int = 0
        self.code:int = 0
        self.image:int = 0
        self.table:int = 0
        self.list:int = 0
        self.link:int = 0
        self.checkbox:int = 0
    
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
                    elif value_type == "image_path":
                        self.add_image(value["image_path"], value["caption"])
                    elif value_type == "table":
                        self.add_table(value["table"], value["columns"], value["rows"])
                    elif value_type == "items":
                        self.add_list(value["items"])
                    elif value_type == "link":
                        self.add_link(value["link"], value["text"])
                    elif value_type == "text_list":
                        self.add_checkbox(value["text_list"], value["checked"])
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

    def __setitem__(self, key:str, section:Union[BaseSection, str, DataFrame, np.ndarray, Figure, List[str]]):
        if len(key) > 0 and key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__setitem__(new_key, section)
        else:
            if isinstance(section, BaseSection):
                return super().__setitem__(key, section)
            elif isinstance(section, str):
                self[key].add_text(section)
            elif isinstance(section, DataFrame):
                self[key].add_table(section)
            elif isinstance(section, np.ndarray):
                self[key].add_table(section)
            elif isinstance(section, Figure):
                self[key].add_image(section)
            elif isinstance(section, list):
                self[key].add_list(section)
            else:
                raise ValueError("Invalid section type.")
    
    def __getitem__(self, key:str) -> BaseSection:
        if len(key) > 0 and key[0] == "/":
            key = key[1:]
        keys = key.split("/")
        if len(keys) > 1:
            ptr, new_key = self.get_section_ptr(keys)
            return ptr.__getitem__(new_key)
        else:
            if key not in self:
                self[key] = Section(self.mdFile, key, self.get_header_location())
            return super().__getitem__(key)
    
    def __delitem__(self, key: str) -> None:     # Need to make this delete all strings with key in it
        if self.section_headers is not None and key in self.section_headers:
            self.section_headers.remove(key)
        return super().__delitem__(key)
    
    def get_header_location(self) -> str:
        """
        Get the heading of the section.

        Returns:
            str: Heading of the section.
        """
        return self.header if self.location == '' or self.location == None else self.location + '/' + self.header

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
        elif isinstance(section, CodeSection):
            name = f"code{self.code}"
        elif isinstance(section, ImageSection):
            name = f"image{self.image}"
        elif isinstance(section, TableSection):
            name = f"table{self.table}"
        elif isinstance(section, ListSection):
            name = f"list{self.list}"
        elif isinstance(section, LinkSection):
            name = f"link{self.link}"
        elif isinstance(section, CheckBoxSection):
            name = f"checkbox{self.checkbox}"
        else:
            raise ValueError("Invalid section type.")
        
        return name
    
    def update_section_count(self, section:BaseSection) -> None:
        """
        Update the section count based on the type of section.

        Args:
            section (BaseSection): Section object to update the count for.
        """
        if isinstance(section, TextSection):
            self.text += 1
            self.section_type_count[SectionType.TEXT] += 1
        elif isinstance(section, CodeSection):
            self.code += 1
            self.section_type_count[SectionType.CODE] += 1
        elif isinstance(section, ImageSection):
            self.image += 1
            self.section_type_count[SectionType.IMAGE] += 1
        elif isinstance(section, TableSection):
            self.table += 1
            self.section_type_count[SectionType.TABLE] += 1
        elif isinstance(section, ListSection):
            self.list += 1
            self.section_type_count[SectionType.LIST] += 1
        elif isinstance(section, LinkSection):
            self.link += 1
            self.section_type_count[SectionType.LINK] += 1
        elif isinstance(section, CheckBoxSection):
            self.checkbox += 1
            self.section_type_count[SectionType.CHECKBOX] += 1
        else:
            raise ValueError("Invalid section type.")
    
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
        if len(heading) > 0 and heading[0] == "/":
            heading = heading[1:]
        headers = heading.split("/") # Split the heading into subheadings
        head = headers[0]

        if len(headers) == 1:  # If there is only one heading left, check if it is this section
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, self.get_header_location())

            if section is not None:
                section = self[head].add_section(None, section)
            else:
                section = self[head]

        elif len(headers) > 1:
            if head not in self.keys():  # If the section does not exist, create it
                self[head] = Section(self.mdFile, head, self.get_header_location())

            section = self[head].add_section("/".join(headers[1:]), section)   # Recursively add the section to the next level
        
        return section
    
    def add_text(self, text:str="\n") -> BaseSection:
        """
        Add a text section to the markdown file.

        Args:
            heading (Optional[str], optional): Heading of the section to add to. Defaults to None.
                - If None, the text is added to the current section.
            text (str): Text to add to the markdown file.

        Returns:
            BaseSection: Text section object.
        """
        section = self.add_section(None, TextSection(self.mdFile, self.get_header_location(), text))
        if section is not None:
            self.text += 1
            self.section_type_count[SectionType.TEXT] += 1
        return section
    
    def add_code(self, code:str="\t", language:str="python") -> BaseSection:
        """
        Add a code section to the markdown file.

        Args:
            code (str): Code to add to the markdown file.
            language (str, optional): Language of the code. Defaults to "python".

        Returns:
            BaseSection: Code section object.
        """
        section = self.add_section(None, CodeSection(self.mdFile, self.get_header_location(), code, language))
        if section is not None:
            self.code += 1
            self.section_type_count[SectionType.CODE] += 1
        return section
    
    def add_figure(self, figure:Union[Figure,str], caption:str=None) -> BaseSection:
        """
        Add a figure section to the markdown file.

        Args:
            figure (Union[Figure,str]): Figure object or path to the figure file.
            caption (str, optional): Caption for the figure. Defaults to None.

        Returns:
            BaseSection: Image section object.
        """
        return self.add_image(figure, caption)
    
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
            image_path = image_path / f"{self.base_name}_image{self.section_type_count[SectionType.IMAGE]}.png"
            figure.savefig(str(image_path), dpi=self.dpi)
            figure = str(image_path)

        section = self.add_section(None, ImageSection(self.mdFile, self.get_header_location(), figure, caption))
        if section is not None:
            self.image += 1
            self.section_type_count[SectionType.IMAGE] += 1
        return section
    
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

        section = self.add_section(None, TableSection(self.mdFile, self.get_header_location(), table, columns, rows))
        if section is not None:
            self.table += 1
            self.section_type_count[SectionType.TABLE] += 1
        return section
    
    def add_list(self, items:list, marked_with:str="-") -> BaseSection:
        """
        Add a list section to the markdown file.

        Args:
            items (list): List of items.

        Returns:
            BaseSection: List section object.
        """
        count = self.add_section(None, ListSection(self.mdFile, self.get_header_location(), items, marked_with))
        if count is not None:
            self.list += 1
            self.section_type_count[SectionType.LIST] += 1
        return count
    
    def add_link(self, link:str, text:Optional[str]) -> BaseSection:
        """
        Add a link section to the markdown file.

        Args:
            link (str): Link to add.
            text (str): Text to display for the link.

        Returns:
            BaseSection: Link section object.
        """
        section = self.add_section(None, LinkSection(self.mdFile, self.get_header_location(), link, text))
        if section is not None:
            self.link += 1
            self.section_type_count[SectionType.LINK] += 1
        return section
    
    def add_checkbox(self, text_list:List[str], checked:Union[List[bool],bool]=False) -> BaseSection:
        """
        Add a checkbox section to the markdown file.

        Args:
            text_list (List[str]): List of text items.
            checked (Union[List[bool],bool], optional): List of booleans indicating if the checkbox is checked. Defaults to False.

        Returns:
            BaseSection: Checkbox section object.
        """
        section = self.add_section(None, CheckBoxSection(self.mdFile, self.get_header_location(), text_list, checked))
        if section is not None:
            self.checkbox += 1
            self.section_type_count[SectionType.CHECKBOX] += 1
        return section
    
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
    

class TextSection(BaseSection):
    """
    Section to render text in the markdown file.
    """
    def __init__(self, mdFile: MdUtils, location:str, text:str):
        """
        Text section to render text in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the text.
            location (str): Location of the text in the markdown file.
            text (str): Text to render in the markdown file.
        """
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
    def __init__(self, mdFile: MdUtils, location:str, code:str, language:str="python"):
        """
        Code section to render code in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the code.
            location (str): Location of the code in the markdown file.
            code (str): Code to render in the markdown file.
            language (str, optional): Language of the code. Defaults to "python".
        """
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
    def __init__(self, mdFile: MdUtils, location:str, image_path:Union[str,Path], caption:Optional[str]=None):
        """
        Image section to render an image in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the image.
            location (str): Location of the image in the markdown file.
            image_path (str): Path to the image file.
            caption (str, optional): Caption for the image. Defaults to None.
        """
        super().__init__(mdFile, location)
        self.image_path:Path = image_path if isinstance(image_path, Path) else Path(image_path)
        self.caption = caption if caption is not None else ""

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        image_path = self.image_path.resolve().relative_to(Path(self.mdFile.file_name).resolve().parent)
        self.mdFile.new_line(self.mdFile.new_inline_image(text=self.caption, path=str(image_path)))
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
        """
        Table section to render a table in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the table.
            location (str): Location of the table in the markdown file.
            table (List[str]): Table data.
            columns (int, optional): Number of columns in the table. Defaults to 3.
            rows (int, optional): Number of rows in the table. Defaults to 3.
        """
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
    def __init__(self, mdFile: MdUtils, location:str, items:list, marked_with:str="-"):
        """
        List section to render a list in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the list.
            location (str): Location of the list in the markdown file.
            items (list): List of items.
        """
        super().__init__(mdFile, location)
        self.items = items
        self.marked_with = marked_with

    def render(self, level:int=1, space_above:bool=False, space_below:bool=True):
        if space_above:
            self.mdFile.new_line()
        self.mdFile.new_list(items=self.items, marked_with=self.marked_with)
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
    def __init__(self, mdFile: MdUtils, location:str, link:str, text:Optional[str]):
        """
        Link section to render a link in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the link.
            location (str): Location of the link in the markdown file.
            link (str): Link to add.
            text (str): Text to display for the link.
        """
        super().__init__(mdFile, location)
        self.link = link
        if text is None:
            self.text = link
        else:
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
        """
        Checkbox section to render a checkbox in the markdown file.

        Args:
            mdFile (MdUtils): Markdown file object to render the checkbox.
            location (str): Location of the checkbox in the markdown file.
            text_list (List[str]): List of text items.
            checked (Union[List[bool],bool], optional): List of booleans indicating if the checkbox is checked. Defaults to False.
        """
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