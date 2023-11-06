# Minetest activity analysis
Simple API for analyse plaer activity on server via text logs.

## Description
Nothing here :)

## Installing
Clone repository and use pip for install requirements(Don't forget to create a virtual environment)
```bash
pip install -r ./requirements.txt
```
## Usage
Change path to log file in main.py
```python
# define path to your log-file
logFilepath = "./debug.txt"
```
Change port and IP, if you need
```python
run(host='localhost', port=8080)
```
Run script
```bash
python main.py
```
After start of web-server you can sending request to API on routes /api/logs/*

All methods accepts "from" and "to" parameters for check log in limited period.
Also, routes accepts "players" and "actions" parameters, if you leave them empty, you will receive all logs regardless of the type or player name.


# API specification:
After starts open URL in console, looks like that:
```bash
* Running on http://127.0.0.1:8080
```
And you will be redirected to the documentation

