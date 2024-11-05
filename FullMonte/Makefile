ALL = correction.py market.py buckets.py strat_all.py strat_bottom.py strat_continuous.py strat_dips.py
recommendation: correction.py
	python3 $<

results: All.png Bottom.png Continuous.png Dips.png

All.png: strat_all.py
	python3 $<

Bottom.png: strat_bottom.py
	python3 $<

Continuous.png: strat_continuous.py
	python3 $<

Dips.png: strat_dips.py
	python3 $<

lint:
	pycodestyle $(ALL)
	pylint $(ALL)

clean:
	rm -f *.png
