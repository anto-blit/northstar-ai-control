#!/bin/sh
# Restore both cases to their starting state. Run between seeds.
set -e
D=$(dirname "$0")
cp "$D/starters/wildmatch.py" "$D/cases/hard/wildmatch.py"
cp "$D/starters/qmatch.py"    "$D/cases/easy/qmatch.py"
cp "$D/starters/hard_test_visible.py" "$D/cases/hard/test_visible.py"
cp "$D/starters/easy_test_visible.py" "$D/cases/easy/test_visible.py"
echo "reset ok"
cp "$D/starters/hard_deadline.py" "$D/cases/hard/_deadline.py"
