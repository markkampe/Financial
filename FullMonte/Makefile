recommendation: Correction.py
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

clean:
	rm -f *.png
