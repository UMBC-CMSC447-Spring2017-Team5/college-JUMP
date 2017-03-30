.PHONY: all

all: diagrams/uml_components.png

diagrams/%.pdf: diagrams/%.tex
	pdflatex --halt-on-error --output-directory diagrams $^

diagrams/%.png: diagrams/%.pdf
	convert -density 300 $^ -quality 90 $@
