# Trove newspapers

This repository contains Jupyter notebooks to work with data from Trove's newspapers zone. For more information see the [Trove Newspapers](https://glam-workbench.net/trove-newspapers/) section of the GLAM Workbench.

## Notebook topics

### Trove newspapers in context

* [**Visualise the total number of newspaper articles in Trove by year and state**](visualise-total-newspaper-articles-by-state-year.ipynb) – explore how Trove's newspaper articles are distributed over time, and by state
* [**Analyse rates of OCR correction**](Analysing_OCR_corrections.ipynb) – explore patterns in OCR text correction; how many corrections are there and where have they been made?
* [**Finding non-English newspapers in Trove**](find-non-english-newspapers.ipynb) – use automated language detection to identify non-English language newspapers in Trove
* [**Beyond the copyright cliff of death**](Beyond_the_copyright_cliff_of_death.ipynb) – find newspapers with content published after 1954

### Visualising searches

* [**QueryPic Deconstructed**](QueryPic_deconstructed.ipynb) – simple app to visualise newspaper searches over time
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

### Get creative

* [**Make composite images from lots of Trove newspaper thumbnails**](Composite-thumbnails.ipynb) – creates thumbnails from a search and compiles them into a mega image
* [**Create 'scissors and paste' messages from Trove newspaper articles**](trove-newspapers-scissors-and-paste.ipynb) – snip words out of page images and compile them into the message of your choice
* [**Create large composite images from snipped words**](trove-newspapers-create-composite-from-words.ipynb) – harvest multiple versions of a list of words and compile them all into one big image

See the [GLAM Workbench for more details](https://glam-workbench.github.io/trove-newspapers/).


## Cite as

See the GLAM Workbench or [Zenodo](https://doi.org/10.5281/zenodo.3521724) for up-to-date citation details.

----

This repository is part of the [GLAM Workbench](https://glam-workbench.github.io/).  
If you think this project is worthwhile, you might like [to sponsor me on GitHub](https://github.com/sponsors/wragge?o=esb).
