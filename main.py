# Streamlit app: E-Commerce Gadget Store Ontology (RDF + SPARQL)
# Bahasa: Indonesian
# Requirements: rdflib, streamlit, pandas
# Run with: pip install rdflib streamlit pandas
# Then: streamlit run streamlit_gadget_store.py

from rdflib import Graph, Namespace, Literal, RDF, RDFS, URIRef
from rdflib.namespace import XSD, FOAF
import streamlit as st
import pandas as pd
import mysql.connector
import os

# -----------------------------
# Konfigurasi
# -----------------------------
RDF_FILE = 'data_gadget.ttl'

# Build ontology graph (in-memory)
# -----------------------------
EX = Namespace("http://example.org/gadgetstore#")
G = Graph()
G.bind('ex', EX)
G.bind('foaf', FOAF)

# Load RDF dari file jika ada
if os.path.exists(RDF_FILE):
    G.parse(RDF_FILE, format='turtle')

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
# Koneksi MySQL dan CRUD
# -----------------------------

def get_conn():
    return mysql.connector.connect(host='localhost', user='root', password='password', database='gadgetstore')

def get_all_brands():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM brand')
    brands = cursor.fetchall()
    conn.close()
    return brands

def get_all_categories():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM category')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_all_products():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM product')
    products = cursor.fetchall()
    conn.close()
    return products

def get_all_customers():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customer')
    customers = cursor.fetchall()
    conn.close()
    return customers

def get_all_orders():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    conn.close()
    return orders

def get_order_contains():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM order_contains')
    oc = cursor.fetchall()
    conn.close()
    return oc

# Fungsi tambah data

def add_brand(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO brand (id) VALUES (%s)', (id,))
    conn.commit()
    conn.close()

def add_category(id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO category (id) VALUES (%s)', (id,))
    conn.commit()
    conn.close()

def add_product(id, label, brand_id, category_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO product (id, label, brand_id, category_id) VALUES (%s, %s, %s, %s)', (id, label, brand_id, category_id))
    conn.commit()
    conn.close()

def add_customer(id, name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO customer (id, name) VALUES (%s, %s)', (id, name))
    conn.commit()
    conn.close()

def add_order(id, customer_id, total_price, order_date):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (id, customer_id, total_price, order_date) VALUES (%s, %s, %s, %s)', (id, customer_id, total_price, order_date))
    conn.commit()
    conn.close()

def add_order_contains(order_id, product_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO order_contains (order_id, product_id) VALUES (%s, %s)', (order_id, product_id))
    conn.commit()
    conn.close()

# Fungsi generate RDF dari data MySQL

def mysql_to_rdf():
    G = Graph()
    G.bind('ex', EX)
    G.bind('foaf', FOAF)
    # Brand
    for b in get_all_brands():
        G.add((EX[b['id']], RDF.type, EX.Brand))
    # Category
    for c in get_all_categories():
        G.add((EX[c['id']], RDF.type, EX.Category))
    # Product
    for p in get_all_products():
        G.add((EX[p['id']], RDF.type, EX.Product))
        if p['label']:
            G.add((EX[p['id']], RDFS.label, Literal(p['label'], datatype=XSD.string)))
        G.add((EX[p['id']], EX.hasBrand, EX[p['brand_id']]))
        G.add((EX[p['id']], EX.belongsToCategory, EX[p['category_id']]))
    # Customer
    for cu in get_all_customers():
        G.add((EX[cu['id']], RDF.type, EX.Customer))
        G.add((EX[cu['id']], FOAF.name, Literal(cu['name'], datatype=XSD.string)))
    # Order
    for o in get_all_orders():
        G.add((EX[o['id']], RDF.type, EX.Order))
        G.add((EX[o['id']], EX.purchasedBy, EX[o['customer_id']]))
        if o['total_price']:
            G.add((EX[o['id']], EX.totalPrice, Literal(float(o['total_price']), datatype=XSD.decimal)))
        if o['order_date']:
            G.add((EX[o['id']], EX.hasDate, Literal(str(o['order_date']), datatype=XSD.date)))
    # Order Contains
    for oc in get_order_contains():
        G.add((EX[oc['order_id']], EX.orderContains, EX[oc['product_id']]))
    return G

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title='Gadget Store Ontology — Demo', layout='wide')
st.title('Demo Ontologi Toko Online Gadget (RDF + SPARQL)')

# Sidebar menu navigasi
menu = st.sidebar.selectbox('Menu', ['Utama', 'Produk', 'Brand', 'Kategori', 'Customer'])

# Helper: ambil data dinamis dari RDF

def get_rdf_entities(rdf_type):
    return [str(s).split('#')[-1] for s in G.subjects(RDF.type, rdf_type)]

def get_rdf_customers():
    return [(str(s).split('#')[-1], str(G.value(s, FOAF.name))) for s in G.subjects(RDF.type, EX.Customer)]

# Tampilkan notifikasi sukses jika ada di session state
if st.session_state.get('notif_success'):
    st.success(st.session_state['notif_success'])
    st.session_state['notif_success'] = ''

if menu == 'Utama':
    # Menu utama: SPARQL kasus dan custom query
    st.subheader('Demo SPARQL Kasus')
    # Form tambah kasus SPARQL dinamis
    with st.expander('Tambah Kasus SPARQL Baru'):
        new_title = st.text_input('Judul Kasus', key='new_case_title')
        new_desc = st.text_area('Deskripsi Kasus', key='new_case_desc')
        new_query = st.text_area('SPARQL Query', key='new_case_query')
        if st.button('Tambah Kasus SPARQL', key='btn_add_case'):
            if new_title and new_query:
                SPARQL_QUERIES[new_title] = {'query': new_query, 'desc': new_desc}
                st.session_state['notif_success'] = f'Kasus "{new_title}" berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Judul dan Query wajib diisi!')
    # Pilihan kasus dinamis
    choice = st.sidebar.selectbox('Pilih Kasus', list(SPARQL_QUERIES.keys()))
    selected = SPARQL_QUERIES[choice]
    st.subheader(choice)
    st.write(selected['desc'])
    try:
        df = run_sparql(selected['query'])
        if df.empty:
            st.info('Tidak ada hasil untuk query ini.')
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f'Error menjalankan query: {e}')

    # Integrasi form tambah data sesuai kasus
    if choice == '1. Produk dan Merek (Brand)':
        st.markdown('---')
        st.subheader('Tambah Produk Baru')
        prod_name = st.text_input('ID Produk (tanpa spasi)', key='prod_id_main')
        prod_label = st.text_input('Nama Produk (Label)', key='prod_label_main')
        brand_options = get_rdf_entities(EX.Brand)
        prod_brand = st.selectbox('Brand', brand_options, key='prod_brand_main')
        cat_options = get_rdf_entities(EX.Category)
        prod_cat = st.selectbox('Kategori', cat_options, key='prod_cat_main')
        if st.button('Tambah Produk', key='btn_prod_main'):
            if prod_name and prod_brand and prod_cat:
                prod_uri = EX[prod_name]
                G.add((prod_uri, RDF.type, EX.Product))
                G.add((prod_uri, EX.hasBrand, EX[prod_brand]))
                G.add((prod_uri, EX.belongsToCategory, EX[prod_cat]))
                if prod_label:
                    G.add((prod_uri, RDFS.label, Literal(prod_label, datatype=XSD.string)))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Produk {prod_name} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Lengkapi semua field produk!')
        st.markdown('---')
        st.subheader('Tambah Brand Baru')
        brand_id = st.text_input('ID Brand (tanpa spasi)', key='brand_id_main')
        if st.button('Tambah Brand', key='btn_brand_main'):
            if brand_id:
                brand_uri = EX[brand_id]
                G.add((brand_uri, RDF.type, EX.Brand))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Brand {brand_id} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Masukkan ID Brand!')
    elif choice == '2. Siapa yang membeli produk tertentu (contoh: iPhone15)':
        # Info jika produk iPhone15 belum ada
        produk_list = get_rdf_entities(EX.Product)
        if 'iPhone15' not in produk_list:
            st.warning('Produk iPhone15 belum ada di RDF. Tambahkan produk iPhone15 terlebih dahulu agar query menghasilkan data.')
        st.markdown('---')
        st.subheader('Tambah Customer Baru')
        cust_id = st.text_input('ID Customer (tanpa spasi)', key='cust_id_main')
        cust_name = st.text_input('Nama Customer', key='cust_name_main')
        if st.button('Tambah Customer', key='btn_cust_main'):
            if cust_id and cust_name:
                cust_uri = EX[cust_id]
                G.add((cust_uri, RDF.type, EX.Customer))
                G.add((cust_uri, FOAF.name, Literal(cust_name, datatype=XSD.string)))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Customer {cust_name} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Masukkan ID dan Nama Customer!')
        st.markdown('---')
        st.subheader('Tambah Order Baru')
        order_id = st.text_input('ID Order (tanpa spasi)', key='order_id_main')
        cust_options = get_rdf_customers()
        cust_select = st.selectbox('Customer', [c[0] for c in cust_options], key='order_cust_main')
        total_price = st.text_input('Total Harga', key='order_total_main')
        order_date = st.text_input('Tanggal (YYYY-MM-DD)', key='order_date_main')
        prod_options = get_rdf_entities(EX.Product)
        order_products = st.multiselect('Produk dalam Order', prod_options, key='order_products_main')
        if st.button('Tambah Order', key='btn_order_main'):
            if order_id and cust_select and total_price and order_date and order_products:
                order_uri = EX[order_id]
                G.add((order_uri, RDF.type, EX.Order))
                G.add((order_uri, EX.purchasedBy, EX[cust_select]))
                G.add((order_uri, EX.totalPrice, Literal(float(total_price), datatype=XSD.decimal)))
                G.add((order_uri, EX.hasDate, Literal(order_date, datatype=XSD.date)))
                for prod in order_products:
                    G.add((order_uri, EX.orderContains, EX[prod]))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Order {order_id} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Lengkapi semua field order dan pilih produk!')
        # Instruksi jika hasil query kosong
        if df.empty:
            st.info('Tidak ada hasil untuk query ini. Pastikan sudah ada produk iPhone15 dan order yang mengandung produk tersebut.')
    elif choice == '3. Produk berdasarkan Kategori (contoh: Laptop)':
        st.markdown('---')
        st.subheader('Tambah Kategori Baru')
        cat_id = st.text_input('ID Kategori (tanpa spasi)', key='cat_id_main')
        if st.button('Tambah Kategori', key='btn_cat_main'):
            if cat_id:
                cat_uri = EX[cat_id]
                G.add((cat_uri, RDF.type, EX.Category))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Kategori {cat_id} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Masukkan ID Kategori!')
        st.markdown('---')
        st.subheader('Tambah Produk Baru')
        prod_name = st.text_input('ID Produk (tanpa spasi)', key='prod_id_main3')
        prod_label = st.text_input('Nama Produk (Label)', key='prod_label_main3')
        brand_options = get_rdf_entities(EX.Brand)
        prod_brand = st.selectbox('Brand', brand_options, key='prod_brand_main3')
        cat_options = get_rdf_entities(EX.Category)
        prod_cat = st.selectbox('Kategori', cat_options, key='prod_cat_main3')
        if st.button('Tambah Produk', key='btn_prod_main3'):
            if prod_name and prod_brand and prod_cat:
                prod_uri = EX[prod_name]
                G.add((prod_uri, RDF.type, EX.Product))
                G.add((prod_uri, EX.hasBrand, EX[prod_brand]))
                G.add((prod_uri, EX.belongsToCategory, EX[prod_cat]))
                if prod_label:
                    G.add((prod_uri, RDFS.label, Literal(prod_label, datatype=XSD.string)))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Produk {prod_name} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Lengkapi semua field produk!')
    elif choice == '4. Daftar Order lengkap (customer, total price, tanggal)':
        st.markdown('---')
        st.subheader('Tambah Customer Baru')
        cust_id = st.text_input('ID Customer (tanpa spasi)', key='cust_id_main4')
        cust_name = st.text_input('Nama Customer', key='cust_name_main4')
        if st.button('Tambah Customer', key='btn_cust_main4'):
            if cust_id and cust_name:
                cust_uri = EX[cust_id]
                G.add((cust_uri, RDF.type, EX.Customer))
                G.add((cust_uri, FOAF.name, Literal(cust_name, datatype=XSD.string)))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Customer {cust_name} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Masukkan ID dan Nama Customer!')
        st.markdown('---')
        st.subheader('Tambah Order Baru')
        order_id = st.text_input('ID Order (tanpa spasi)', key='order_id_main4')
        cust_options = get_rdf_customers()
        cust_select = st.selectbox('Customer', [c[0] for c in cust_options], key='order_cust_main4')
        total_price = st.text_input('Total Harga', key='order_total_main4')
        order_date = st.text_input('Tanggal (YYYY-MM-DD)', key='order_date_main4')
        prod_options = get_rdf_entities(EX.Product)
        order_products = st.multiselect('Produk dalam Order', prod_options, key='order_products_main4')
        if st.button('Tambah Order', key='btn_order_main4'):
            if order_id and cust_select and total_price and order_date and order_products:
                order_uri = EX[order_id]
                G.add((order_uri, RDF.type, EX.Order))
                G.add((order_uri, EX.purchasedBy, EX[cust_select]))
                G.add((order_uri, EX.totalPrice, Literal(float(total_price), datatype=XSD.decimal)))
                G.add((order_uri, EX.hasDate, Literal(order_date, datatype=XSD.date)))
                for prod in order_products:
                    G.add((order_uri, EX.orderContains, EX[prod]))
                G.serialize(destination=RDF_FILE, format='turtle')
                st.session_state['notif_success'] = f'Order {order_id} berhasil ditambahkan!'
                st.rerun()
            else:
                st.warning('Lengkapi semua field order dan pilih produk!')

    st.markdown('---')
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

elif menu == 'Produk':
    st.header('Data Produk')
    produk = []
    for s in G.subjects(RDF.type, EX.Product):
        label = G.value(s, RDFS.label)
        brand = G.value(s, EX.hasBrand)
        cat = G.value(s, EX.belongsToCategory)
        produk.append({
            'ID': str(s).split('#')[-1],
            'Label': str(label) if label else '',
            'Brand': str(brand).split('#')[-1] if brand else '',
            'Kategori': str(cat).split('#')[-1] if cat else ''
        })
    if produk:
        st.dataframe(pd.DataFrame(produk))
    else:
        st.info('Belum ada produk.')
    st.subheader('Tambah Produk Baru')
    prod_name = st.text_input('ID Produk (tanpa spasi)', key='prod_id')
    prod_label = st.text_input('Nama Produk (Label)', key='prod_label')
    brand_options = get_rdf_entities(EX.Brand)
    cat_options = get_rdf_entities(EX.Category)
    prod_brand = st.selectbox('Brand', brand_options, key='prod_brand')
    prod_cat = st.selectbox('Kategori', cat_options, key='prod_cat')
    if st.button('Tambah Produk'):
        if prod_name and prod_brand and prod_cat:
            prod_uri = EX[prod_name]
            G.add((prod_uri, RDF.type, EX.Product))
            G.add((prod_uri, EX.hasBrand, EX[prod_brand]))
            G.add((prod_uri, EX.belongsToCategory, EX[prod_cat]))
            if prod_label:
                G.add((prod_uri, RDFS.label, Literal(prod_label, datatype=XSD.string)))
            G.serialize(destination=RDF_FILE, format='turtle')
            st.session_state['notif_success'] = f'Produk {prod_name} berhasil ditambahkan!'
            st.rerun()
        else:
            st.warning('Lengkapi semua field produk!')

elif menu == 'Brand':
    st.header('Data Brand')
    brand_list = get_rdf_entities(EX.Brand)
    if brand_list:
        st.dataframe(pd.DataFrame({'Brand': brand_list}))
    else:
        st.info('Belum ada brand.')
    st.subheader('Tambah Brand Baru')
    brand_id = st.text_input('ID Brand (tanpa spasi)', key='brand_id')
    if st.button('Tambah Brand'):
        if brand_id:
            brand_uri = EX[brand_id]
            G.add((brand_uri, RDF.type, EX.Brand))
            G.serialize(destination=RDF_FILE, format='turtle')
            st.session_state['notif_success'] = f'Brand {brand_id} berhasil ditambahkan!'
            st.rerun()
        else:
            st.warning('Masukkan ID Brand!')

elif menu == 'Kategori':
    st.header('Data Kategori')
    cat_list = get_rdf_entities(EX.Category)
    if cat_list:
        st.dataframe(pd.DataFrame({'Kategori': cat_list}))
    else:
        st.info('Belum ada kategori.')
    st.subheader('Tambah Kategori Baru')
    cat_id = st.text_input('ID Kategori (tanpa spasi)', key='cat_id')
    if st.button('Tambah Kategori'):
        if cat_id:
            cat_uri = EX[cat_id]
            G.add((cat_uri, RDF.type, EX.Category))
            G.serialize(destination=RDF_FILE, format='turtle')
            st.session_state['notif_success'] = f'Kategori {cat_id} berhasil ditambahkan!'
            st.rerun()
        else:
            st.warning('Masukkan ID Kategori!')

elif menu == 'Customer':
    st.header('Data Customer')
    cust_list = get_rdf_customers()
    if cust_list:
        st.dataframe(pd.DataFrame(cust_list, columns=['ID', 'Nama']))
    else:
        st.info('Belum ada customer.')
    st.subheader('Tambah Customer Baru')
    cust_id = st.text_input('ID Customer (tanpa spasi)', key='cust_id')
    cust_name = st.text_input('Nama Customer', key='cust_name')
    if st.button('Tambah Customer'):
        if cust_id and cust_name:
            cust_uri = EX[cust_id]
            G.add((cust_uri, RDF.type, EX.Customer))
            G.add((cust_uri, FOAF.name, Literal(cust_name, datatype=XSD.string)))
            G.serialize(destination=RDF_FILE, format='turtle')
            st.session_state['notif_success'] = f'Customer {cust_name} berhasil ditambahkan!'
            st.rerun()
        else:
            st.warning('Masukkan ID dan Nama Customer!')

# -----------------------------
# Load dan Simpan RDF
# -----------------------------
st.markdown('---')
if st.checkbox('Tampilkan RDF (Turtle)'):
    turtle = G.serialize(format='turtle')
    if isinstance(turtle, bytes):
        turtle = turtle.decode('utf-8')
    st.code(turtle, language='turtle')
