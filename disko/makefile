clean:
	rm -rf dist/ build/ disko.spec __pycache__/ disko.html disko.rpt disko.log
setup:
	pip install -r requirements.txt

dist: 
	pyinstaller -Fw disko.py

rel:
	mkdir ryan; cp ~/lib/python/ryan/*.py ryan/
	git add ryan; git commit . 
