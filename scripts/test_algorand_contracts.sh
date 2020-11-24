
git clone https://github.com/algorand/smart-contracts.git

cd smart-contracts || exit 255

for target in $(find . -name "*.teal");
do
    if ! tealer $target; then
        echo "tests failed"
        exit 1
    fi
done
exit 0


