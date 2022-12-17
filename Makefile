requirements: requirements.txt
	pip3 install -r requirements.txt
	make run
run: main.py
	python3 main.py