## Setup Environment - Virtual Environment
### 1. Buat Virtual Environment

```
python -m venv revisi_dicoding

```
### 2. Aktifkan Virtual Environment

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\revisi_dicoding\Scripts\activate
```

### 3. Instalasi Dependencies

```
pip freeze > requirements.txt
pip install -r requirements.txt
```
## Setup Environment - Shell/Terminal
```
mkdir Revisi Dicoding
cd Revisi Dicoding
python -m venv revisi_dicoding
.\revisi_dicoding\Scripts\activate
pip freeze > requirements.txt
pip install -r requirements.txt

```

## Run steamlit app
```
streamlit run Proyek_dicoding_streamlit.py
```
