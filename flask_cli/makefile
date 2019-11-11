.PHONY: clean

dist: *.py app/*.py
	pyinstaller -F cli.py
clean: 
	rm -rf build dist

adminlte:
	cd $(VIRTUAL_ENV)/../pkg/AdminLTE-*/; cp -rfv dist pages plugins bower_components $(VIRTUAL_ENV)/../app/static/; # sed -e 's/(href|src)="((pages|plugins|dist|bower_components)[^"]\+\)"/\1="{{url_for(\'static\',filename=\'\2\')}}"/'
