# Streamlit app: E-Commerce Gadget Store Ontology (RDF + SPARQL)
# Bahasa: Indonesian
# Requirements: rdflib, streamlit, pandas
# Run with: pip install rdflib streamlit pandas
# Then: streamlit run streamlit_gadget_store.py

from rdflib import Graph, Namespace, Literal, RDF, RDFS, URIRef
from rdflib.namespace import XSD, FOAF
import streamlit as st
import pandas as pd

# -----------------------------
# Build ontology graph (in-memory)
# -----------------------------
EX = Namespace("http://example.org/gadgetstore#")
G = Graph()
G.bind('ex', EX)
G.bind('foaf', FOAF)

# Classes
G.add((EX.Product, RDF.type, RDFS.Class))
G.add((EX.Category, RDF.type, RDFS.Class))
G.add((EX.Brand, RDF.type, RDFS.Class))
G.add((EX.Customer, RDF.type, RDFS.Class))
G.add((EX.Order, RDF.type, RDFS.Class))

# Properties
G.add((EX.hasBrand, RDF.type, RDF.Property))
G.add((EX.belongsToCategory, RDF.type, RDF.Property))
G.add((EX.purchasedBy, RDF.type, RDF.Property))
G.add((EX.orderContains, RDF.type, RDF.Property))
G.add((EX.hasPrice, RDF.type, RDF.Property))
G.add((EX.hasDate, RDF.type, RDF.Property))
G.add((EX.totalPrice, RDF.type, RDF.Property))

# Sample data: Brands
G.add((EX.Apple, RDF.type, EX.Brand))
G.add((EX.Samsung, RDF.type, EX.Brand))
G.add((EX.Dell, RDF.type, EX.Brand))

# Categories
G.add((EX.Smartphone, RDF.type, EX.Category))
G.add((EX.Laptop, RDF.type, EX.Category))
G.add((EX.Accessory, RDF.type, EX.Category))

# Products
G.add((EX.iPhone15, RDF.type, EX.Product))
G.add((EX.GalaxyS24, RDF.type, EX.Product))
G.add((EX.XPS13, RDF.type, EX.Product))
G.add((EX.Mouse_X1, RDF.type, EX.Product))

# Link products -> brand and category
G.add((EX.iPhone15, EX.hasBrand, EX.Apple))
G.add((EX.iPhone15, EX.belongsToCategory, EX.Smartphone))
G.add((EX.GalaxyS24, EX.hasBrand, EX.Samsung))
G.add((EX.GalaxyS24, EX.belongsToCategory, EX.Smartphone))
G.add((EX.XPS13, EX.hasBrand, EX.Dell))
G.add((EX.XPS13, EX.belongsToCategory, EX.Laptop))
G.add((EX.Mouse_X1, EX.hasBrand, EX.Apple))
G.add((EX.Mouse_X1, EX.belongsToCategory, EX.Accessory))

# Customers
G.add((EX.Rendi, RDF.type, EX.Customer))
G.add((EX.Dita, RDF.type, EX.Customer))
G.add((EX.Ahmad, RDF.type, EX.Customer))
G.add((EX.Rendi, FOAF.name, Literal('Rendi', datatype=XSD.string)))
G.add((EX.Dita, FOAF.name, Literal('Dita', datatype=XSD.string)))
G.add((EX.Ahmad, FOAF.name, Literal('Ahmad', datatype=XSD.string)))

# Orders
G.add((EX.ORD001, RDF.type, EX.Order))
G.add((EX.ORD002, RDF.type, EX.Order))
G.add((EX.ORD003, RDF.type, EX.Order))

# Order details: who purchased, contains product, date, price
G.add((EX.ORD001, EX.purchasedBy, EX.Rendi))
G.add((EX.ORD001, EX.orderContains, EX.iPhone15))
G.add((EX.ORD001, EX.hasDate, Literal('2025-10-01', datatype=XSD.date)))
G.add((EX.ORD001, EX.totalPrice, Literal(12000000, datatype=XSD.decimal)))

G.add((EX.ORD002, EX.purchasedBy, EX.Dita))
G.add((EX.ORD002, EX.orderContains, EX.XPS13))
G.add((EX.ORD002, EX.orderContains, EX.Mouse_X1))
G.add((EX.ORD002, EX.hasDate, Literal('2025-10-05', datatype=XSD.date)))
G.add((EX.ORD002, EX.totalPrice, Literal(25000000, datatype=XSD.decimal)))

G.add((EX.ORD003, EX.purchasedBy, EX.Ahmad))
G.add((EX.ORD003, EX.orderContains, EX.GalaxyS24))
G.add((EX.ORD003, EX.hasDate, Literal('2025-10-07', datatype=XSD.date)))
G.add((EX.ORD003, EX.totalPrice, Literal(10000000, datatype=XSD.decimal)))

# -----------------------------
# SPARQL queries (4 kasus utama)
# -----------------------------
SPARQL_QUERIES = {
    '1. Produk dan Merek (Brand)': {
        'query': '''
PREFIX ex: <http://example.org/gadgetstore#>
SELECT ?product ?brand WHERE {
  ?product a ex:Product .
  ?product ex:hasBrand ?brand .
}
''',
        'desc': 'Menampilkan semua produk beserta brand/mereknya.'
    },
    '2. Siapa yang membeli produk tertentu (contoh: iPhone15)': {
        'query': '''
PREFIX ex: <http://example.org/gadgetstore#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?customerName ?order WHERE {
  ?order a ex:Order .
  ?order ex:orderContains ex:iPhone15 .
  ?order ex:purchasedBy ?customer .
  ?customer foaf:name ?customerName .
}
''',
        'desc': 'Menampilkan nama customer yang membeli produk iPhone15 beserta nomor order.'
    },
    '3. Produk berdasarkan Kategori (contoh: Laptop)': {
        'query': '''
PREFIX ex: <http://example.org/gadgetstore#>
SELECT ?product WHERE {
  ?product a ex:Product .
  ?product ex:belongsToCategory ex:Laptop .
}
''',
        'desc': 'Menampilkan produk yang termasuk kategori Laptop.'
    },
    '4. Daftar Order lengkap (customer, total price, tanggal)': {
        'query': '''
PREFIX ex: <http://example.org/gadgetstore#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?order ?customerName ?total ?date WHERE {
  ?order a ex:Order .
  ?order ex:purchasedBy ?customer .
  ?customer foaf:name ?customerName .
  OPTIONAL { ?order ex:totalPrice ?total }
  OPTIONAL { ?order ex:hasDate ?date }
}
''',
        'desc': 'Menampilkan semua order beserta nama customer, total harga, dan tanggal pembelian.'
    }
}

# helper untuk menjalankan query dan mengembalikan DataFrame

def run_sparql(q):
    qres = G.query(q)
    cols = [str(v) for v in qres.vars]
    rows = []
    for row in qres:
        rows.append([str(x) if x is not None else '' for x in row])
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows, columns=cols)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title='Gadget Store Ontology — Demo', layout='wide')
st.title('Demo Ontologi Toko Online Gadget (RDF + SPARQL)')
st.markdown('Pilih salah satu kasus di sidebar untuk menjalankan SPARQL. Kamu juga dapat memasukkan query SPARQL custom.')

choice = st.sidebar.selectbox('Pilih Kasus', list(SPARQL_QUERIES.keys()))
selected = SPARQL_QUERIES[choice]

st.subheader(choice)
st.write(selected['desc'])

# run and show
try:
    df = run_sparql(selected['query'])
    if df.empty:
        st.info('Tidak ada hasil untuk query ini.')
    else:
        st.dataframe(df)
except Exception as e:
    st.error(f'Error menjalankan query: {e}')

st.markdown('---')
# show turtle
if st.checkbox('Tampilkan RDF (Turtle)'):
    turtle = G.serialize(format='turtle')
    # rdflib may return str or bytes depending on version
    if isinstance(turtle, bytes):
        turtle = turtle.decode('utf-8')
    st.code(turtle, language='turtle')

# custom SPARQL runner
st.subheader('Jalankan SPARQL custom')
user_q = st.text_area('Masukkan SPARQL query di sini', value='''PREFIX ex: <http://example.org/gadgetstore#>\nSELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 50''', height=160)
if st.button('Jalankan query'):
    try:
        df2 = run_sparql(user_q)
        if df2.empty:
            st.info('Query berjalan tetapi tidak mengembalikan hasil.')
        else:
            st.dataframe(df2)
    except Exception as e:
        st.error(f'Error menjalankan SPARQL: {e}')

st.markdown('---')
st.caption('Contoh sederhana: dapat dikembangkan menjadi sistem perpustakaan/ toko online nyata dengan menyimpan triples ke file TTL atau menghubungkan ke SPARQL endpoint.')
