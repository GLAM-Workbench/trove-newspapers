# Trove newspapers

This repository contains Jupyter notebooks to work with data from Trove's newspapers zone. For more information see the [Trove Newspapers](https://glam-workbench.net/trove-newspapers/) section of the GLAM Workbench.

## Notebook topics

### Trove newspapers in context

* [**Visualise the total number of newspaper articles in Trove by year and state**](visualise-total-newspaper-articles-by-state-year.ipynb) – explore how Trove's newspaper articles are distributed over time, and by state
* [**Analyse rates of OCR correction**](Analysing_OCR_corrections.ipynb) – explore patterns in OCR text correction; how many corrections are there and where have they been made?
* [**Finding non-English newspapers in Trove**](find-non-english-newspapers.ipynb) – use automated language detection to identify non-English language newspapers in Trove
* [**Beyond the copyright cliff of death**](Beyond_the_copyright_cliff_of_death.ipynb) – find newspapers with content published after 1954
* [**Gathering historical data about the addition of newspaper titles to Trove**](historical-data-newspaper-titles.ipynb) – find when newspaper titles were added to Trove by extracting lists from web archives

### Visualising searches

* [**QueryPic**](querypic.ipynb) – simple app to visualise newspaper searches over time, this is the latest version with many new features
* [**QueryPic Deconstructed**](QueryPic_deconstructed.ipynb) – an older version of QueryPic that lets you build queries using keywords, states, or newspapers
* [**Visualise Trove newspaper searches over time**](visualise-searches-over-time.ipynb) – use facets to slice up newspaper search results and visualise over time
* [**Map Trove newspaper results by state**](Map-newspaper-results-by-state.ipynb) – create a choropleth map to visualise search results by state
* [**Map Trove newspaper results by place of publication**](Map-newspaper-results-by-place-of-publication.ipynb) – links newspapers to their place of publication and maps the results
* [**Map Trove newspaper results by place of publication over time**](Map-newspaper-results-by-place-of-publication-over-time.ipynb) – adds a time dimension to the example above

### Useful tools

* [**Save a Trove newspaper article as an image**](Save-Trove-newspaper-article-as-image.ipynb) – grabs the page on which an article was published, and then crops the page image to the boundaries of the article to create a complete, intact image of the article as it was originally published
* [**Download a page image**](Save-page-image.ipynb) – a simple app that lets you download page images as complete, high-resolution JPG files
* [**Generate an article thumbnail**](Get-article-thumbnail.ipynb) – generate a nice square thumbnail image for a newspaper article
* [**Upload Trove newspaper articles to Omeka-S**](Upload-Trove-newspapers-to-Omeka.ipynb) – steps through the process of uploading Trove newspaper articles to your own Omeka-S instance via the API
* [**Harvest Australian Women's Weekly covers (or the front pages of any newspaper)**](harvest-aww-covers-and-newspaper-front-pages.ipynb) – harvest the front pages of any newspaper, including covers from the Australian Women's Weekly

### Tips and tricks

* [**Today’s news yesterday**](Todays-news-yesterday.ipynb) – uses the `date` index and the `firstpageseq` parameter to find articles from exactly 100 years ago that were published on the front page
* [**Create a Trove OCR corrections ticker**](Create-a-Trove-corrections-ticker.ipynb) – uses the `has:corrections` parameter to get the total number of newspaper articles with OCR corrections
* [**Get a list of Trove newspapers that doesn't include government gazettes**](Get_newspaper_titles_not_including_gazettes.ipynb) – workaround for a problem with the `newspaper/titles` endpoint of the API
* [**Get the page coordinates of a digitised newspaper article from Trove**](trove-newspapers-get-coordinates-of-articles.ipynb) – demonstrates how to find the coordinates of a newspaper article on a digitised page

### Get creative

* [**Make composite images from lots of Trove newspaper thumbnails**](Composite-thumbnails.ipynb) – creates thumbnails from a search and compiles them into a mega image
* [**Create 'scissors and paste' messages from Trove newspaper articles**](trove-newspapers-scissors-and-paste.ipynb) – snip words out of page images and compile them into the message of your choice
* [**Create large composite images from snipped words**](trove-newspapers-create-composite-from-words.ipynb) – harvest multiple versions of a list of words and compile them all into one big image

See the [GLAM Workbench for more details](https://glam-workbench.github.io/trove-newspapers/).

### Data files

* CSV formatted lists of newspaper titles in Trove
  * [trove_newspaper_titles_2009_2021.csv](trove_newspaper_titles_2009_2021.csv) – complete dataset of captures and titles
  * [trove_newspaper_titles_first_appearance_2009_2021.csv](trove_newspaper_titles_first_appearance_2009_2021.csv) – filtered dataset, showing only the first appearance of each title / place / date range combination
  * There is also an [alphabetical list of newspaper titles](https://gist.github.com/wragge/7d80507c3e7957e271c572b8f664031a), showing approximately when they first appeared in Trove.
* [CSV formatted list of Australian Women's Weekly issues, 1933 to 1982](data/aww-issues.csv)
* [Australian Women's Weekly front covers, 1933 to 1982](https://cloudstor.aarnet.edu.au/plus/s/NaKjoKNFOGXXDNN) (2,566 images on Cloudstor)
For easy browsing, I've compiled the images into a set of PDF files, one for each decade, available from Dropbox:
  * [1933 to 1939](https://www.dropbox.com/s/0j6zpeuw6tbey5k/aww-1933-1939.pdf?dl=0)
  * [1940 to 1949](https://www.dropbox.com/s/y1he8dd6h655weu/aww-1940-1949.pdf?dl=0)
  * [1950 to 1959](https://www.dropbox.com/s/i9gp9i51nofmlqo/aww-1950-1959.pdf?dl=0)
  * [1960 to 1969](https://www.dropbox.com/s/2of63tovcnphijo/aww-1960-1969.pdf?dl=0)
  * [1970 to 1979](https://www.dropbox.com/s/f2yxpg8u4dx5uf2/aww-1970-1979.pdf?dl=0)
  * [1980 to 1982](https://www.dropbox.com/s/xanohtas1fi7eu4/aww-1980-1982.pdf?dl=0)
* [Trove newspapers with non-English language content](https://gist.github.com/wragge/9aa385648cff5f0de0c7d4837896df97)
* [Trove newspapers with articles published after 1954](newspapers_post_54.csv)


## Cite as

See the GLAM Workbench or [Zenodo](https://doi.org/10.5281/zenodo.3521724) for up-to-date citation details.

----

This repository is part of the [GLAM Workbench](https://glam-workbench.github.io/).  
If you think this project is worthwhile, you might like [to sponsor me on GitHub](https://github.com/sponsors/wragge?o=esb).
