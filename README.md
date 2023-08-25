<p align="center">
	<img src="assets/icon.png"/><br>
</p>

# toloka2python [![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)

<p align="center">
<img src="https://img.shields.io/github/languages/code-size/CakesTwix/toloka2python?style=for-the-badge"/>
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
<img src="https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white"/><br><br>
<a href="https://www.buymeacoffee.com/cakestwix"><img width="150" src="https://img.buymeacoffee.com/button-api/?text=Buy me a tea&emoji=🍵&slug=cakestwix&button_colour=FF5F5F&font_colour=ffffff&font_family=Poppins&outline_colour=000000&coffee_colour=FFDD00" /></a>
</p>

Python library for getting information from Ukrainian torrent tracker Toloka. 
> Note: The library is still under development and may not work in other places

## Installing from git
```bash
pip install git+https://github.com/CakesTwix/toloka2python
```

> I don't want to upload to PyPi at the moment, I need to add more functionality first

## Usage/Examples

1. Authorization and getting information about yourself
	```python
	from toloka2python import Toloka

	toloka = Toloka("Username", "Password")
	print(toloka.me)
	```
2. Search torrents by title
	```python
	for torrent in toloka.search("Магія"):
	  print(torrent.url)
	```
3. Getting information about another user
	```python
	print(toloka.get_account("https://toloka.to/u123456"))
	```
4. Getting information about torrent
	```python
	print(toloka.get_torrent("https://toloka.to/t71117"))
	```
## Authors

- [@CakesTwix](https://www.github.com/CakesTwix)

## License

- [GPL-v3](https://choosealicense.com/licenses/gpl-3.0/)

