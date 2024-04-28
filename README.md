# neira
http://mattdailis.github.io/neira/

This is a project to help coaches and rowers keep track of how their school is doing compared to other schools in the NEIRA conference.

# build process
1. Make a virtualenv
2. In that environment, pip install -r requirements.txt
3. python neira_scraper/scrape.py
4. python neira_dot/read.py
5. cd neira_ui
6. npm install
7. npm run build
8. cd ..
9. rm -rf docs
10. mv ./neira_ui/build docs
11. mv ./dot ./docs