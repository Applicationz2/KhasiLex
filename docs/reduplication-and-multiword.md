# Khasi Reduplication and Multiword Architecture

KhasiLex does not treat adjacent repeated words as accidental duplicates.

Structural examples include:

- `biang biang`
- `wut wut`
- `kloi kloi`

These are stored as `entry_type=reduplication` with metadata for base form, token count, reduplication type and pattern, grammatical function, semantic relation, definitions/translations, examples, register/dialect, provenance and review status.

The starter dataset deliberately does not guess the meaning of unverified reduplicative forms.

## NLP behaviour

The tokenizer preserves Unicode text and character offsets. The reduplication detector recognizes exact adjacent patterns such as `X X` and `X X X`, while the phrase matcher recognizes lexicalized multiword entries from the master lexicon.

This allows an AI system to distinguish accidental duplicate text, productive Khasi reduplication, lexicalized reduplicative expressions and ordinary multiword phrases.
