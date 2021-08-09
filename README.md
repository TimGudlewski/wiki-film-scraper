# wiki-film-scraper
wiki-film-scraper is a tool for creating a JSON file containing film details. It uses Beautiful Soup to scrape Wikipedia.

## Usage
### Quick Start
Import the **Scraper** class from the **wfs** package. Define an instance of the class. 
```python
from wfs import Scraper

my_scraper = Scraper()
```
Call **set_choices** on the instance and pass the films you want to search into the **choices** parameter as a list. 
```python
choices = [{'name': 'behind green lights', 'year': '1946'}, {'name': 'opening night', 'year': '1977'}]
my_scraper.set_choices(choices=choices)
```
The choices parameter can be a list of strings, or a list of dictionaries with 'name' and 'year' properties. 
Include a release year for each film title to avoid unwanted search results.

Call **set_films** to search the films and set them to the 'films' attribute of the Scraper instance.
Call **save_films** to save the films and their details to a JSON file.
```python
my_scraper.set_films()
my_scraper.save_films()
```
By default, they save to a file named *example.json* in a directory *wfs_output* in your *home* directory.
