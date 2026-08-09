# Image-to-EpubConverter
A converter intended for Image extensions to Epub or PDF, designed for ereaders


A Python tool for turning a folder of images into a single EPUB ebook or PDF document.

It is designed for image-based content:
 - Manga and Comics
 - Manwha and Webtoons
 - Scanned books and documents
 - Photo albums
 - Any other collection of ordered immages

Can be used either through a gui or from the command line.

<br>


<br>

## Installation 
Python3 is required.

```bash
pip install pillow img2pdf
git clone https://github.com/22-Rendor/Image-to-EpubConverter.git
cd Image-to-EpubConverter
python3 img2epub.py
```

## CLI Usage

### Creating an EPUB

```bash
python img2epub.py <format> <directory> [options]
```

The two formats are:

`epub` or `pdf`

Available options:

| `-o`, `--output` | Specify the output filename/path |
| `-t`, `--title` | Specify the title of the newly formatted item |

Example:

```bash
python img2epub.py epub "E:\path\to\folder"
```

This will create:

```text
E:\path\to\folder.epub
```

Custom Output Location:

```bash
python img2epub.py epub "E:\path\to\folder" -o "E:\new\saved\epub\path.epub"
```
<br>

### GUI Usage
The GUI provides a simple way to convert your images without using the command line.
1. Open img2epub.py
2. Click Browse... and select your image folder.
3. (Optional) Enter a title for your EPUB.
4. Select EPUB or PDF.
5. Convert.
<br>
The newly created file will be saved in the saem location as the selected folder.<br><br>

## Folder Structure
The Program supports two different folder layouts:

### 1. Flat Folder

   The Simple option is to put all images directly inside one folder:
```
   My Album/
   ├── 001.jpg
   ├── 002.jpg
   ├── 003.jpg
   ├── 004.jpg
   └── 005.jpg
```

   Running the coverter on My Album/ created one book containing all five images in the same directory of MyAlbum/

   For Example:
   ```
   /../My Album/ 
```
   becomes: 

```
   My Album.epub
   or
   My Album.pdf
```

### 2. Nested Folders

   You can also organize images into subfolders

   Each subfolder becomes a section/chapter of the EPUB:

```
   Scanned book/
   ├──  Chapter 1/ 
   │ ├── 001.jpg
   │ ├── 002.jpg
   │ └── 003.jpg
   │ ├── Chapter 2/
   │ ├── 001.jpg
   │ ├── 002.jpg
   │ └── 003.jpg
   │ └── Chapter 3/
   ├── 001.jpg
   ├── 002.jpg
   └── 003.jpg
```

   Resulting EPUb contains:
   - Chapter 1
   - Chapter 2
   - Chapter 3


<br>

   
