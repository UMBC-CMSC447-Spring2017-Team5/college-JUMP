.PHONY: all

all: diagrams/uml_components.png diagrams/uml_models_class.png

diagrams/%.png: diagrams/%.tex
	pdflatex --halt-on-error --output-directory diagrams $^
	convert -density 300 $(^:.tex=.pdf) -quality 90 $@
