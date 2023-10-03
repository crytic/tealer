#!/usr/bin/env bash

git clone https://github.com/algorand/smart-contracts.git

cd smart-contracts || exit 255

while IFS= read -r -d '' target
do
    if ! tealer print human-summary --contracts "$target" > /dev/null; then
        echo "tests failed"
        exit 1
    fi
    if ! tealer detect --contracts "$target" > /dev/null; then
        echo "tests failed"
        exit 1
    fi
done < <(find . -name "*.teal" -print0)
exit 0


