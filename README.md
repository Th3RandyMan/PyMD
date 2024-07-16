PyMD
==================

[![License](https://img.shields.io/badge/license-MIT-black.svg)](https://opensource.org/licenses/MIT)

# Overview
This packages provides an intuitive way to generate markdown files. While sweeping over parameters for a project, results can be neatly organized and stored within a markdown file.

# Features
* Index over subsections
* Assign multiple section types to each section
* Add text, images, figures, lists, tables, checkboxes, and hyperlinks to the markdown.
* Save and load as JSON

# Installation
## Pip
Use pip to install PyMD:
```bash
pip install .
```  

# Markdown File Examples

## Create MDGenerator Object
When creating the `MDGenerator` Object, either the save path and filename can be given together in the `save_path` or separately. If given together, this will neglect the `file_name` parameter, and the file descriptor must be given with the `save_path`. File descriptor is not needed if `file_name` is given separately.

A list of authors can be provided or a single name. It will be formatted accordingly.

```python
from PyMD import MDGenerator

md = MDGenerator(save_path="folder/filename.md", title="Title of MD file", author="John Smith")

# Add sections to the md object

# Save when done to generate md file
md.save()
```  

## Create and Index Section Headers
Section headers are automatically created when a section get or set is made. Levels or subsections can be addressed by a file system format. Examples would be:

### Indexing using base object
```python
md.add_text("Section 1/Subsection 1/Subsubsection 1","This is placed in the subsubsection of the first section and first subsection.")
```  

### Dictionary Single Indexing
```python
md["Section 1/Subsection 1/Subsubsection 1"].add_text("This is placed in the subsubsection of the first section and first subsection.")
```  

### Dictionary Multi Indexing
```python
md["Section 1"]["Subsection 1"]["Subsubsection 1"].add_text("This is placed in the subsubsection of the first section and first subsection.")
```  

### Variation of Single and Multi Indexing
```python
md["Section 1/Subsection 1"]["Subsubsection 1"].add_text("This is placed in the subsubsection of the first section and first subsection.")
```  
However, indexing through a function call can only be done by the base object. Not a membering object.

## Assignment Functions
Each function will have its own parameters, but the provided functions are the following:
```python
md.add_text(text)
md.add_code(text)
md.add_figure(figure)
md.add_image(image_path)
md.add_table(table)
md.add_list(text_list)
md.add_link(link, text)
md.add_checkbox(text_list, checked)
```  

## Default Assignments
To speed up common assignments, text, figures, tables, and lists are allowed to be assigned to the dictionary. For examples, each assignment can be made to add to a section:

### Text Assignmnet
```python
md["Section 1"]["Subsection 1"]["Subsubsection 1"] = "This is placed in the subsubsection of the first section and first subsection."
```  

### Figure Assignment
```python
from matplotlib import pyplot as plt

fig, ax = plt.subplots()
# Add to the figure
md["Figure or Image Section"] = fig
```

### Dataframe Assignment
```python
from pandas import DataFrame

# Create array instance with or without columns
table = DataFrame(array, columns=columns)
md["Table Section"] = table
```

### Numpy Assignment
```python
import numpy

# Create array instance
md["Table Section"] = array
```

### List Assignment
```python
md["List Section"] = ["Item 1", "Item 2", "Item 3"]
```

## Save and Load JSON file
```python
md.save_json()
```
```python
md.save_json(new_file_name)
```

```python
md = MDGenerator(save_path=json_file_location)
md.load_json()
```
```python
md = MDGenerator()
md.load_json(json_file_location)
```
