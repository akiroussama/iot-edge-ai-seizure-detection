PYTHON ?= uv run python

.PHONY: test lint demo smoke smoke-train report all-checks clean package

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

demo:
	$(PYTHON) scripts/run_synthetic_demo.py

smoke:
	$(PYTHON) -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru

smoke-train: smoke

report:
	$(PYTHON) scripts/make_report.py --synthetic --out-dir reports

all-checks: test lint demo report smoke-train

package:
	$(PYTHON) -m pytest -q
	$(PYTHON) -m ruff check .
	$(PYTHON) scripts/run_synthetic_demo.py

clean:
	rm -rf .pytest_cache .ruff_cache reports/synthetic_demo
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
