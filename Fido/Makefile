ALL = income.py positions.py

lint:
	pycodestyle $(ALL)
	# data filtering code is similar between both modules
	pylint -d R0801 $(ALL)
