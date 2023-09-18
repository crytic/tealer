#!/usr/bin/env bash

git clone https://github.com/algorand/smart-contracts.git

cd smart-contracts || exit 255

while IFS= read -r -d '' target
do
    if ! tealer --contracts "$target" --print human-summary > /dev/null; then
        echo "tests failed"
        exit 1
    fi
done < <(find . -name "*.teal" -print0)
exit 0


