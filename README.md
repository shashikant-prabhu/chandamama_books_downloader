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
2. Run the downloader and specify the directory where you would like the files
   saved. On Windows you can point it at your `D:` drive:
   ```bash
   python download_chandamama_books.py D:\\ChandamamaBooks
   ```

The script crawls pages starting from `https://www.chandamama.in/story/` looking
for links containing `englishview.php`. It downloads each linked PDF and stores
it in a folder named after the corresponding year.

**Note:** This repository cannot verify the availability or legality of the
content. Ensure that downloading these files complies with the website's terms
of service and all applicable laws.
