import os
import re
from ebooklib import epub
import locale

# Ensure proper locale for sorting numeric strings (if needed)
locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')

def sort_naturally(files):
    """Sort files naturally, considering both numeric and non-numeric parts of the filename."""
    def try_int(value):
        try:
            return int(value)
        except ValueError:
            return value

    def alphanumeric_key(file_name):
        return [try_int(c) for c in re.split(r'(\d+)', file_name)]

    return sorted(files, key=alphanumeric_key)

def txt_to_epub(folder_path, epub_file, title="Untitled", author="Unknown"):
    # Create a new eBook object
    book = epub.EpubBook()

    # Add metadata for the eBook using add_metadata
    book.add_metadata('DC', 'title', title)  # Add the title
    book.add_metadata('DC', 'creator', author)  # Add the author

    # List all txt files in the folder
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]

    # Sort the files naturally (numerically and alphabetically)
    txt_files = sort_naturally(txt_files)

    # List to store chapter items
    chapter_items = []

    for idx, txt_file in enumerate(txt_files, start=1):
        # Construct the full path to the txt file
        file_path = os.path.join(folder_path, txt_file)

        # Read the chapter content from the file
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text_content = file.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try reading with a different encoding (e.g., 'windows-1252' or 'latin-1')
            print(f"UTF-8 decoding failed. Trying 'windows-1252' encoding for {txt_file}...")
            with open(file_path, 'r', encoding='windows-1252') as file:
                text_content = file.read()

        # Create a chapter title based on the filename (use the filename without the extension)
        chapter_title = txt_file.replace('.txt', '')

        # Create a new chapter (this will be the content of the chapter)
        chapter_html = epub.EpubHtml(title=chapter_title, file_name=f"chapter{idx}.xhtml", lang="en")

        # Wrap the content in HTML structure, handle line breaks correctly
        html_content = """
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>{}</title>
        </head>
        <body>
            <h1>{}</h1>
            <p>{}</p>
        </body>
        </html>
        """.format(chapter_title, chapter_title, text_content.replace('\n', '<br/>'))

        # Set the content of the chapter using the 'content' attribute
        chapter_html.content = html_content

        # Add chapter to the book
        book.add_item(chapter_html)
        chapter_items.append(chapter_html)

    # Define the table of contents (TOC)
    book.toc = tuple([epub.Link(chapter.file_name, chapter.title, chapter.title) for chapter in chapter_items])

    # Add necessary eBook items
    book.add_item(epub.EpubNav())  # Navigation

    # Write the eBook to a file
    epub.write_epub(epub_file, book)

    print(f"ePub file has been created: {epub_file}")

# Example usage
folder_path = "downloads/wandering_inn"
epub_file = "downloads/output.epub"
txt_to_epub(folder_path, epub_file, title="wandering inn", author="jkhon")
