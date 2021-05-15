from .app import app
import re


newlines = re.compile(r"\s*\n\s*") # J'entoure de \s optionnel pour nettoyer un peu en même temps.

@app.template_filter("split_new_lines")
def split_new_lines(text):
	return newlines.split(text)
