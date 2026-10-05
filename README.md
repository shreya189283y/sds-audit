# SDS Audit

A tool that audits school district Safety Data Sheets (SDS) against authoritative chemical hazard lists and flags products of concern.

Status: in development.

## How it works

1. Extract ingredients and CAS numbers from Section 3 of each SDS.
2. Match each CAS number against published hazard lists.
3. Assign a concern level using fixed, documented rules.
4. Flag products with undisclosed or trade secret ingredients.

Every flag cites its source list. No concern level is assigned by an AI model.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest
```

## Project structure

```
src/        core code (extraction, hazard lookup, scoring)
scripts/    command line runners
tests/      unit tests
data/       SDS files, hazard lists, results
docs/       scoring rules, validation, limitations
```

## Limitations

An SDS does not list every ingredient. Low concentration ingredients and trade secret ingredients can be withheld. This tool can only assess what is disclosed.