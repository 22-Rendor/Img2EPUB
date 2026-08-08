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

   
