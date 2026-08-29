## Summary

Describe the change and why it is needed.

## Change type

- [ ] Software / API
- [ ] Dictionary / lexical data
- [ ] Khasi grammar / morphology
- [ ] Translation / multilingual mapping
- [ ] Documentation / standards
- [ ] Build / CI / deployment

## Lexical-data checklist

Complete this section when lexical, grammatical, pronunciation, or translation data changes.

- [ ] Khasi spelling and Unicode NFC were checked.
- [ ] Khasi diacritics were preserved.
- [ ] Polysemous meanings use separate senses where necessary.
- [ ] Reduplicative or multiword constructions are not flattened into ordinary duplicate tokens.
- [ ] Source and licence/provenance are recorded.
- [ ] AI-generated content remains pending until human review.
- [ ] `verified` status is used only for reviewed material.

## Validation

- [ ] `python scripts/validate.py`
- [ ] `python scripts/build_all.py`
- [ ] `pytest -q`
- [ ] Docker build, when deployment behavior changed
