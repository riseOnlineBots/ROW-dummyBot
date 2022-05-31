[Tesserac](https://github.com/UB-Mannheim/tesseract/wiki) is required.


git filter-branch --index-filter 'git rm --cached --ignore-unmatch tesseract/libtesseract-5.dll' --tag-name-filter cat -- --all