PYTHON ?= uv run python

.PHONY: test lint demo smoke smoke-train report all-checks clean package msg-label-audit-sheet msg-label-audit-check msg-horizon-viability

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

msg-label-audit-sheet:
	$(PYTHON) scripts/make_label_audit_review_sheet.py \
		--audit reports/msg_full_label_audit.csv \
		--out reports/msg_label_audit_review_sheet.csv \
		--max-events 12

msg-label-audit-check:
	$(PYTHON) scripts/check_label_audit_review.py \
		--review-sheet reports/msg_label_audit_review_sheet.csv \
		--out reports/msg_label_audit_review_check.csv \
		--min-events 5

msg-horizon-viability:
	$(PYTHON) scripts/summarize_horizon_viability.py \
		--windows data/processed/msg/windows_1h.parquet \
		--events data/processed/msg/events.parquet \
		--out-csv reports/msg_horizon_viability.csv \
		--out-md reports/msg_horizon_viability.md \
		--sph-minutes 5 60 \
		--sop-minutes 30 360 1440 \
		--postictal-exclusion-minutes 240 \
		--postictal-anchor seizure_start \
		--title "MSG Horizon Viability"

all-checks: test lint demo report smoke-train

package:
	$(PYTHON) -m pytest -q
	$(PYTHON) -m ruff check .
	$(PYTHON) scripts/run_synthetic_demo.py

clean:
	rm -rf .pytest_cache .ruff_cache reports/synthetic_demo
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
