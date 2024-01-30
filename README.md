# RAG Demo POC

## How To

1.  Put `.env` file to the same folder as this readme file
2.  Put `data.parquet.gzip` file to the `data` folder. You might need to create the `data` folder.
3.  Run following commands in the same folder as this readme file is:

```r
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run src/Home.py
```

4.  Now if you open your browser and type `localhost:3000` the chatbot app should start working
