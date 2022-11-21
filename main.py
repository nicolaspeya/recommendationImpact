import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from google.cloud import bigquery
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import JsCode

# overflow-wrap: break-word;
#    white-space: break-spaces;
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)
st.markdown("""
<style>

.stApp {
        background-image: url("./peyaimage.jpg");
        background-size: cover;
        }

.table-title {
    font-size:18px !important;
}

div[data-baseweb="radio"] > div {
    color: black;
}


div[data-testid="metric-container"] {
   background-color: rgba(28, 131, 225, 0.1);
   border: 1px solid rgba(28, 131, 225, 0.1);
   padding: 5% 5% 5% 10%;
   border-radius: 5px;
   color: rgb(30, 103, 119);
   overflow-wrap: break-word;
}

section[data-testid="stSidebar"] > div:first-of-type {
background-color: rgb(93, 192, 207);
background: rgb(93, 192, 207);
padding-top:-20px;
margin-top:-20px;
box-shadow: -2rem 0px 2rem 2rem rgba(0,0,0,0.16);


.sidebar .sidebar-content {
    background-image: linear-gradient(#2e7bcf,#2e7bcf);
    color: green;

 #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}


/* breakline for metric text         */
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
   
   color: red;
}
</style>
"""
, unsafe_allow_html=True)


# Create API client.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials)



st.title("Análisis de Impacto Herramienta Recomendados")
st.write("El objetivo del análisis es visualizar y evaluar el impacto en productos y ordenes que tuvo la Reco Tool desde mediados de Octubre 2022 hasta mediados de Noviembre 2022")

# padding-top:-20px;
# margin-top:-20px;
# '<p class= "table-title" style= font-size: 600, 

# st.write('<p class= "table-title" style= font-size: 600, "color: black">Detalle de Ordenes de Productos Recomendados Agregados a Catálogo de Partners</p>', unsafe_allow_html=True)

st.sidebar.markdown("<p style= 'font-size:30px; padding-top:-40px; margin-top:-40px'>Navigation</p>", unsafe_allow_html=True)

if 'buttonClick' not in st.session_state:
    st.session_state.disabled = True
  

if 'partnerInfo' not in st.session_state:
    st.session_state.partnerdisabled = True

if 'partnerSelection' not in st.session_state:
    st.session_state.partnerselection = False

def radiostatus():
    currentStatus = st.session_state.disabled

    if st.session_state.disabled == True:
        st.session_state.disabled = False
        if st.session_state.partnerdisabled == False:
            st.session_state.partnerdisabled = True

    else:
        st.session_state.disabled = True
   

    return st.session_state.disabled #,  st.session_state.partnerdisabled

def partnerstatus():
    partnerStatus = st.session_state.partnerdisabled

    if st.session_state.partnerdisabled == True:
        st.session_state.partnerdisabled = False
        if st.session_state.disabled == False:
            st.session_state.disabled = True
    else:
        st.session_state.partnerdisabled = True


    return st.session_state.partnerdisabled


st.sidebar.button('Principales Insights 👇', on_click=radiostatus, key='buttonClick')

partners = ["Partners con Mayores Ventas", "Partners sin Ventas", "Productos con Mayores Ventas","Productos sin Ventas en el Período"]

choices = st.sidebar.radio("Partners", partners, help='Partners que agregaron productos del TOP 500 a su Catálogo en el Período Considerado',  disabled=st.session_state.disabled)

st.sidebar.write('\n')
st.sidebar.write('\n')
partners_ratio = ["Partner Orders", "Top Partners Ratio", "Lowest Partners Ratio"]

st.sidebar.button('Partners Orders-KPI 👇', on_click=partnerstatus, key='partnerInfo')
partner_choices = st.sidebar.radio('Partners Orders-KPI', partners_ratio, help = 'Ver Info a Nivel Partner sobre Órdenes y Conversión de Productos en Órdenes', disabled=st.session_state.partnerdisabled)

st.sidebar.write('\n')
st.sidebar.button('Conclusions 👈')
st.sidebar.write('\n')
with st.sidebar.expander("Consideraciones Importantes"):
     st.write(""" 
    - La herramienta se encuentra disponible en todos los países de LATAM.
    - Se amplió el alcance de la herramienta, incorportando la Vertical Farmacias en todos los países.
    - Para el análisis se toman en cuenta los productos nuevos que agregan los partners, así como
      los productos que encienden en sus menues. 
    - El universo de Partners que se considera en el análisis, son los partners que tuvieron una 
      descarga del archivo Excel en el sitio de productos Recomendados así como los partners que recibieron el mail
      con el archivo de prodcutos recomendados e hicieron click en el archivo. 
     """) 



#file = "C:/Users/nicolas.ferrari/Documents/RecoToolOctubre.csv"
#file = "C:/Users/nicolas.ferrari/Documents/rowordersdata.xlsx"
file = "./files/rowordersdata_v2.xlsx"
productsWithoutSalesfile = "./files/productsSinVentas.xlsx"

partner_file = "./files/products_orders_by_partner.xlsx"

#file = "C:/Users/nicolas.ferrari/Documents/VP_dataRecoTool.csv"
# Perform query.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.cache(allow_output_mutation=True)
def run_query(query):
    query_job = client.query(query)
    rows_raw = query_job.result()
    # Convert to list of dicts. Required for st.experimental_memo to hash the return value.
    rows = [dict(row) for row in rows_raw]

    data = pd.DataFrame(rows)
    return data


query = '''select country, businessCategory, partner_id, partner_name, count(distinct(gtin)) as products  from `peya-food-and-groceries.user_nicolas_ferrari.recommendationImpacts`

where currentDate = DATE('2022-11-14')

group by country, businessCategory, partner_id, partner_name

order by products desc '''

@st.cache()
def load_orders_data(file,file_2, file_3):


    orders_data = pd.read_excel(file,engine="openpyxl")
#   orders_data = pd.read_csv(file, sep=';')

    products_data = pd.read_excel(file_2, engine="openpyxl")

    partner_data = pd.read_excel(file_3, engine="openpyxl")
    
    # Los que tienen Null value en la columna Quantity, son los que no tuvieron ventas. 
    # En el notebook se joinean los productos que agregan los partners y los productos que tuvieron 
    # ordenes. Los que dan null son los que no tienen ordenes.
    products_data = products_data[pd.isnull(products_data['Quantity'])]

    return orders_data, products_data, partner_data

@st.cache()
def get_metrics():
  
    products_data = run_query(query)
    newProducts = products_data['products'].sum()

    partnersWithNewProducts = len(products_data['partner_id'].unique())

    orders = load_orders_data(file,productsWithoutSalesfile, partner_file)[0]
    
    totalOrders = len(orders['orderId'].unique())
    gmvUSD = orders['valueUS'].sum()

  #partnersWithOrders = len(orders['partnerId'].unique())

    return partnersWithNewProducts, newProducts, totalOrders, gmvUSD


partnersWithNewProducts = get_metrics()[0]
newProducts = get_metrics()[1]
totalOrders = get_metrics()[2]
GMV = get_metrics()[3]



data = load_orders_data(file, productsWithoutSalesfile, partner_file)

orders_products = data[0]

non_orders_products = data[1]

partners_data = data[2]


gb = GridOptionsBuilder.from_dataframe(orders_products)
gridOptions = gb.build()
gb.configure_pagination()



if st.session_state.disabled == True and st.session_state.partnerdisabled == True and not st.session_state.partnerselection:
    countries = orders_products['country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()
    #l2 = []
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    partners = orders_products['partnerName'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    countries = orders_products['country'].unique().tolist()
    l2 = countries[:]
   # countries_selected = col1.multiselect('Countries', l2, default=countries)

    if "All Partners" in partner:
        
        # col1, col2, col3, col4 = st.columns(4)
        # col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
        # col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
        # col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
        # col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con nuevas Ordenes')
       
        countries_selected = col5.multiselect('', l2, default=countries)
        orders_products = orders_products[orders_products['country'].isin(countries_selected)]
        
       
        #partner = col2.selectbox('Check For Specific Partner', l3, index= default_ix)
    
    else:
        st.session_state.partnerselection = True
        orders_products = orders_products[orders_products['partnerName'] == partner]
        countries = orders_products['country'].unique().tolist()
        countries_selected = col5.multiselect('Countries', l2, default=countries)

    
    if not partner:
        countries_selected = col1.multiselect('', l2, default=countries)
        orders_products = orders_products[orders_products['country'].isin(countries_selected)]
        col6.selectbox('Check For Specific Partner', partners)
        col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
        col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
        col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
        col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')
   

partners_ratio = ['Partner Orders', 'Top Partners Ratio', 'Lowest Partners Ratio']

partners = ["Partners con Mayores Ventas", "Partners sin Ventas", "Productos con Mayores Ventas","Productos sin Ventas en el Período"]

jscode = JsCode(""" 
            function(params) {
                
                if (params.node.rowIndex % 2  === 0) {
                 
                    return {
                        
                        'backgroundColor': "#D8F2FF"
                    }
                    }
                    }
                    """)


if st.session_state.disabled == False and choices == "Partners con Mayores Ventas":
    
    #top_partners = orders_products.groupby(['country','partnerId','partnerName']).sum('valueUS').reset_index()
    top_partners = orders_products.groupby(['country','partnerId','partnerName']).agg({'valueUS': 'sum', 'totalValue': 'sum', 'Quantity':'sum','gtin': 'nunique', 'orderId':'nunique'}).reset_index()
    #orders_products = orders_products[orders_products['country'].isin(countries_selected)]
    
    top_partners = top_partners.rename(columns={'gtin':'Products','orderId':'Orders'})

    #top_partners['orders'] = orders_products.groupby(['country','partnerId','partnerName']).size().values
    print(top_partners)

    print(top_partners.columns)
    top_partners['valueUS'] = round(top_partners['valueUS'])

    top_partners = top_partners.sort_values('valueUS',ascending=False)[0:30]

    top_partners = top_partners[['country','partnerName','partnerId','valueUS','totalValue','Quantity','Orders','Products']]  #.drop('gtin',axis=1)

    top_partners = top_partners.rename(columns={'country':'Country','partnerName':'Partner','partnerId':'PartnerID', 'valueUS': 'SalesValueUSD','totalValue': 'SalesValueLC','Quantity':'SalesQuantity'})

    partnersWithNewProducts = len(top_partners['PartnerID'].unique())
    newProducts = top_partners['Products'].sum()
    totalOrders = top_partners['Orders'].sum()
    GMV = top_partners['SalesValueUSD'].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    partners = top_partners['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #print(top_partners.columns)
    countries = top_partners['Country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)

    # top_partners = top_partners.rename(columns = {"totalValue":'valueLC'})
    
    st.write('<p class= "table-title" style= font-size: 600, "color: black">Top 30 Partners con mayores ventas en el Período</p>', unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(top_partners)
    gridOptions = gb.build()
    gb.configure_pagination()
    gridOptions['getRowStyle'] = jscode

    AgGrid(top_partners, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

elif st.session_state.disabled == False and choices == "Partners sin Ventas":

    
    partners_sin_ventas = orders_products[orders_products['orderId'] == 0][['country','partnerId','partnerName','gtin','Product']]
    
    partner_sin_ventas_grouped = partners_sin_ventas.groupby(['partnerName']).agg({'partnerId':'sum','gtin':'nunique','Product':'nunique'})
    countries = partners_sin_ventas['country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    partnersWithNewProducts = len(partner_sin_ventas_grouped)
    newProducts = partner_sin_ventas_grouped['Product'].sum()
    totalOrders = 0
    GMV = 0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')
    #l2 = []
    l2 = countries[:]

    partners_sin_ventas = partners_sin_ventas.rename(columns={'country':'Country','partnerName':'Partner','partnerId':'PartnerID', 'gtin':'Gtin'}) 

    partners = partners_sin_ventas['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)

    countries_selected = col5.multiselect('', l2, default=countries)
    gb = GridOptionsBuilder.from_dataframe(partners_sin_ventas)
    gridOptions = gb.build()
    gb.configure_pagination()

    gridOptions['getRowStyle'] = jscode

    st.write('<p class= "table-title" style= font-size: 600, "color: black">Partners que no tuvieron ventas en el Período</p>', unsafe_allow_html=True)
    AgGrid(partners_sin_ventas, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

elif st.session_state.disabled == False and choices == "Productos con Mayores Ventas":
    
    top_products = orders_products.groupby(['country','partnerName','partnerId','Product','gtin']).sum()
    top_products['orders'] = orders_products.groupby(['country','partnerName','partnerId', 'Product', 'gtin']).size().values

    top_products = top_products.reset_index()

    
   
    #top_products = top_products.reset_index()
    total_products_orders = len(top_products)
    
    top_sellers = int(0.2 * total_products_orders)
    top_products = top_products.sort_values('valueUS',ascending=False)[0:top_sellers]

    partnersWithNewProducts = len(top_products['partnerId'].unique())
    newProducts =  top_sellers#orders_products[orders_products.isin(partnersWithNewProducts)] #.groupby('partnerId').nunique('gtin')['gtin'].sum()
    totalOrders = top_products['orders'].sum()
    GMV = top_products['valueUS'].sum()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    countries = top_products['country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()
    
    top_products = top_products[['Product','gtin', 'valueUS',  'totalValue' , 'orders',  'Quantity', 'partnerName','partnerId','country']]

    top_products = top_products.rename(columns={'gtin':'Gtin','country':'Country','partnerName':'Partner','partnerId':'PartnerID', 'orders':'Orders', 'valueUS': 'SalesValueUSD','totalValue': 'SalesValueLC','Quantity':'SalesQuantity'})

    partners = top_products['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)
    #top_products = top_products.rename(columns = {"totalValue":'valueLC'})

    gb = GridOptionsBuilder.from_dataframe(top_products)
    gridOptions = gb.build()
    gb.configure_pagination()
    gridOptions['getRowStyle'] = jscode

    st.write('<p class= "table-title" style= font-size: 600, "color: black">Vendor Products con mayores Ventas en el Período(Top 20%)</p>', unsafe_allow_html=True)
    AgGrid(top_products, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)


elif st.session_state.disabled == False and choices == "Productos sin Ventas en el Período":

   

    non_orders_products = non_orders_products[['product_name','gtin', 'partner_Name', 'partnerId', 'country','businessCategory']] 
    
    countries = non_orders_products['country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    partnersNewProducts = non_orders_products['partnerId'].nunique()
    newProducts = non_orders_products.groupby(['partnerId','gtin']).size().values.sum()
    GMV = 0
    non_orders_products = non_orders_products.rename(columns={'product_name':'Product','gtin':'Gtin', 'businessCategory':'Category','country':'Country','partner_Name':'Partner','partnerId':'PartnerID', 'orders':'Orders', 'valueUS': 'SalesValueUSD','totalValue': 'SalesValueLC','Quantity':'SalesQuantity'})


    totalOrders = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    #l2 = []
    l2 = countries[:]

    partners = non_orders_products['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)

    #countries_selected = st.multiselect('', l2, default=countries)
    gb = GridOptionsBuilder.from_dataframe(non_orders_products)
    gridOptions = gb.build()
    gb.configure_pagination()
    
    gridOptions['getRowStyle'] = jscode
    
    st.write('<p class= "table-title" style= font-size: 600, "color: black">Vendor Products que no tuvieron Ventas</p>',  unsafe_allow_html=True)

    AgGrid(non_orders_products, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

#partners_ratio = ['Partner Orders', 'Top Partners Ratio', 'Lowest Partners Ratio']
elif st.session_state.disabled == True and st.session_state.partnerdisabled == False and partner_choices == 'Partner Orders':
    #country	businessCategory	partnerId	partnerName	ratio	newProducts	numberOfOrders
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')
    
    partner_data = partners_data.rename(columns={'numberOfOrders':'Orders'}) 

    partner_data['ratio'] = round(partner_data['ratio'],2)
    partner_data = partner_data.sort_values('Orders',ascending=False)
  
    countries = partner_data['country'].unique().tolist()

    partner_data = partner_data[['partnerName', 'partnerId', 'Orders','newProducts','ratio', 'country','businessCategory']] 

    partner_data = partner_data.rename(columns={'businessCategory':'Category','country':'Country','ratio':'Ratio', 'newProducts':'Products', 'partnerName':'Partner','partnerId':'PartnerID'})

    partners = partner_data['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    #l2 = []
   # l2 = countries[:]

   # countries_selected = col6.multiselect('', l2, default=countries)

    gb = GridOptionsBuilder.from_dataframe(partner_data)
    gridOptions = gb.build()
    gb.configure_pagination()
    gridOptions['getRowStyle'] = jscode
    
    st.write('<p class= "table-title" style= font-size: 600, "color: black">Ordenes y Nuevos Productos Totales por Partner</p>',  unsafe_allow_html=True)

    AgGrid(partner_data, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

elif st.session_state.disabled == True and st.session_state.partnerdisabled == False and partner_choices == 'Top Partners Ratio':
    

    #l2 = []
   
    
    partner_data = partners_data.rename(columns={'numberOfOrders':'Orders'}) 

    partner_data['ratio'] = round(partner_data['ratio'],2)
    partner_data = partner_data.sort_values('ratio',ascending=False)[0:15]
    #GMV = partner_data['valueUS'].sum()
    partners = partner_data['partnerId'].unique().tolist()

    GMV = orders_products[orders_products['partnerId'].isin(partners)]['valueUS'].sum()

    partner_data = partner_data[['partnerName', 'partnerId', 'ratio', 'Orders','newProducts', 'country','businessCategory']] 
    countries = partner_data['country'].unique().tolist()
    partner_data = partner_data.rename(columns={'businessCategory':'Category','country':'Country','ratio':'Ratio', 'newProducts':'Products', 'partnerName':'Partner','partnerId':'PartnerID'})

    
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    partnersWithNewProducts = partner_data['PartnerID'].nunique()
    newProducts = partner_data['Products'].sum()
    totalOrders = int(partner_data['Orders'].sum())
    

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    partners = partner_data['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)
    l2 = countries[:]

   # countries_selected = st.multiselect('', l2, default=countries)

   
    gb = GridOptionsBuilder.from_dataframe(partner_data)
    gridOptions = gb.build()
    gb.configure_pagination()
    
    gridOptions['getRowStyle'] = jscode
   
    st.write('<p class= "table-title" style= font-size: 600, "color: black">Top 15 de Partners con Mejor ratio de Nuevas Ordenes por Producto Agregado</p>',  unsafe_allow_html=True)
    AgGrid(partner_data, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

elif st.session_state.disabled == True and st.session_state.partnerdisabled == False and partner_choices == 'Lowest Partners Ratio':
    
    partner_data = partners_data.rename(columns={'numberOfOrders':'Orders'}) 

    
    countries = partner_data['country'].unique().tolist()
    #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()

    partner_data['ratio'] = round(partner_data['ratio'],2)
    partner_data = partner_data.sort_values('ratio')[0:15]

    partners = partner_data['partnerId'].unique().tolist()
    GMV = orders_products[orders_products['partnerId'].isin(partners)]['valueUS'].sum()

    partner_data = partner_data[['partnerName', 'partnerId', 'ratio', 'Orders','newProducts', 'country','businessCategory']] 

    partner_data = partner_data.rename(columns={'businessCategory':'Category','country':'Country','ratio':'Ratio', 'newProducts':'Products', 'partnerName':'Partner','partnerId':'PartnerID'})


    partnersWithNewProducts = partner_data['PartnerID'].nunique()
    newProducts = partner_data['Products'].sum()
    totalOrders = int(partner_data['Orders'].sum())
    

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Partners", partnersWithNewProducts, help='Partners que agregaron productos')
    col2.metric("Productos", newProducts, help='Nuevos Vendor Products en Catálogo de Partners')
    col3.metric("Ordenes Totales", totalOrders, help='Ordenes Totales generados con los Productos Agregados')
    col4.metric("GMV USD", round(GMV), help='Total GMV en USD generado con Nuevos Productos')

    #l2 = []
    l2 = countries[:]

    partners = partner_data['Partner'].unique().tolist()
    l3 = []
    l3 = partners[:]
    l3.insert(0, "All Partners")
    #l3.append('All Partners')
    default_ix = l3.index('All Partners')
        
    col5,col6 = st.columns([3,1])
    partner = col6.selectbox('Check For Specific Partner', l3, index= default_ix)
    #l2 = []
    l2 = countries[:]

    countries_selected = col5.multiselect('', l2, default=countries)

    #countries_selected = st.multiselect('', l2, default=countries)

   
   
    st.write('<p class= "table-title" style= font-size: 600, color: blue>15 Partners con menor ratio de Nuevas Ordenes por Producto Agregado</p>', unsafe_allow_html=True)
    gb = GridOptionsBuilder.from_dataframe(partner_data)
    gridOptions = gb.build()
    gb.configure_pagination()
    
    gridOptions['getRowStyle'] = jscode
    
    AgGrid(partner_data, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True)

else:

    orders_products = orders_products.rename(columns= {'totalValue':'valueLC'})    
    print(orders_products.columns)
    orders_products = orders_products[['country','businessCategory_','partnerId','partnerName', 'Product','gtin', 'valueUS','valueLC','Quantity','orderId']]
    
    orders_products = orders_products.rename(columns={'businessCategory_':'Category','country':'Country', 'gtin':'Gtin', 'partnerName':'Partner','partnerId':'PartnerID','valueUS': 'ValueUSD', 'valueLC':'ValueLC', 'orderId': 'OrderID'})

    # countries = orders_products['country'].unique().tolist()
    # #citieslist = data[data['country_name'] == selected_country]['city'].unique().tolist()
    # #l2 = []
    # l2 = countries[:]
    # countries_selected = st.multiselect('Countries', l2, default=countries)
    # orders_products = orders_products[orders_products['country'].isin(countries_selected)]
    
    st.write('<p class= "table-title" style= font-size: 600, "color: black">Detalle de Ordenes de Productos Recomendados Agregados a Catálogo de Partners</p>', unsafe_allow_html=True)

    gb = GridOptionsBuilder.from_dataframe(orders_products)
    gridOptions = gb.build()
    gb.configure_pagination()
    gridOptions['getRowStyle'] = jscode

    AgGrid(orders_products, height=500,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
   # custom_css=custom_css,
    allow_unsafe_jscode=True)


#st.write(products_data)
# # Print results.
# st.write("Some wise words from Shakespeare:")
# for row in rows:
#     st.write("✍️ " + row['word'])
