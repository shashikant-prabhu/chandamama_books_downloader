# chandamama_books_downloader

This repository contains a simple script to crawl the chandamama.in story site
and download available PDF issues of Chandamama magazine. Files are organised by
year in the output directory.

## Usage

1. Install the required Python packages (for example using a virtual
environment):
   ```bash
   pip install requests beautifulsoup4
   ```
2. Run the downloader, providing the year you wish to download and the base
   directory where the files should be stored. The script creates a folder
   named `chandamama_books_<year>` inside the given directory. On Windows you
   can point it at your `D:` drive:
   ```bash
   python download_chandamama_books.py 2010 D:\\
   ```

   If you simply want to list the download URLs without fetching the files,
   add the `--list-only` flag:
   ```bash
   python download_chandamama_books.py 2010 D:\\ --list-only
   ```

The script crawls pages starting from `https://www.chandamama.in/story/` looking
for links containing `englishview.php`. Only English PDF files for the
requested year are downloaded and placed in the
`chandamama_books_<year>` directory. Each request uses a two minute timeout and
progress is logged to the console with an estimated download time for each
file.

For safety the downloader verifies that each file advertises a PDF
`Content-Type` header before saving it.

**Note:** This repository cannot verify the availability or legality of the
content. Ensure that downloading these files complies with the website's terms
of service and all applicable laws.
