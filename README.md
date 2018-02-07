Python TV listing application for Google App Engine
---------------------------------------------------
The application is divided in 2 main parts:

1. Scraper for getting tv shows information (titles, channel, times, etc). Scraping is scheduled every day at 00:00
2. Web API for retrieving information about shows.

Deployment using the gcloud command line tool:

`gcloud app deploy index.yaml cron.yaml app.yaml`
