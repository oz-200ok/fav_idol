set -eo pipefail

echo "Starting isort"
poetry run isort .
echo "OK"

echo "Starting black"
poetry run black .
echo "OK"



echo "All tests passed successfully!"