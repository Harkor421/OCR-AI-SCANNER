import openai
import json
import re
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image, ImageEnhance
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("API_PASSWORD")
pytesseract.pytesseract.tesseract_cmd = os.getenv("PYTESSERACT_LOCATION")
openai.api_key = os.getenv("OPEN_AI_API_KEY")

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the PDF Text Extraction API."

@app.route('/process', methods=['POST'])
def process_pdf():
    api_key = request.headers.get('X-Api-Key')
    if api_key != SECRET_KEY:
        return jsonify({'error': 'Unauthorized'}), 401

    pdf_file = request.files['pdfFile']

    # Save the uploaded PDF file temporarily
    pdf_file_path = 'temp.pdf'
    pdf_file.save(pdf_file_path)

    extracted_text = extract_text_from_pdf(pdf_file_path)
    gpt_response_1 = interact_with_gpt(extracted_text)
    gpt_response_2 = interact_with_gpt_2(extracted_text)


    # Extract category data and articles
    category_data = extract_and_jsonify_data(gpt_response_1)
    articles = extract_and_filter_articles(gpt_response_2)
 


    # Combine category data and articles into a single JSON object
    result = { "":category_data, "articulos": articles}

    return jsonify(result)

def extract_and_jsonify_data(input_text):
    # Split the input text into lines and extract key-value pairs
    lines = input_text.strip().split('\n')
    category_data = {}
    for line in lines:
        key, value = [part.strip() for part in line.split(':', 1)]
        category_data[key] = value

    return category_data

def extract_and_filter_articles(input_text):
    # Split the input text into lines and extract key-value pairs
    lines = input_text.strip().split('\n')

    # Initialize variables
    articles = []

    for line in lines:
        # Split each line into key-value pairs
        pairs = line.strip().split(', ')
        current_article = {}

        for pair in pairs:
            key, value = [part.strip() for part in pair.split(': ')]
            
            # Remove slashes that are accompanied by a quote to the left
            value = value.strip('"').replace('\\"', '"')

            current_article[key] = value

        # Add the article to the list
        articles.append(current_article)

    return articles



def extract_text_from_pdf(pdf_file_path):
    images = convert_from_bytes(open(pdf_file_path, 'rb').read())
    extracted_text = []
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,#-/@()'

    for img in images:
        img = img.rotate(0, expand=True)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.35)
        text = pytesseract.image_to_string(img, config=custom_config, lang='eng')
        extracted_text.append(text)

    extracted_text_combined = "\n".join(extracted_text)
    return extracted_text_combined

def interact_with_gpt(prompt): #This can be modified to any prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="""De este texto que es de Colombia extrae el identificacion_proveedor (NIT O DOCUMENTO DE IDENTIDAD), nombre_proveedor, correo_proveedor, contacto_proveedor, direccion_proveedor, telefono_proveedor, 
        codigo_cotizacion_proveedor (NUMERO IDENTIFICATIVO DE LA COTIZACIÓN POR PARTE DEL PROVEEDOR), tiempo_vigencia (EN DIAS), forma_pago (CONTADO ,CRÉDITO, ANTICIPO, POR CUOTAS), metodo_pago (TARJETA, TRANSFERENCIA BANCARIA, EFECTIVO, ONLINE), 
        condicion_pago (SEGUN FORMA PAGO, EJEMPLO 60% ANTICIPO, 40% CONTRAENTREGA), condiciones_entrega (INSTALADO, IR A RECOGER, PUESTO EN SITIO CON PAGO FLETE, PUESTO EN SITIO SIN PAGO FLETE), tiempo_entrega (TIEMPO DE ENTREGA EN DIAS), costo_transporte, direccion_web. Cabe destacar que esto es un documento pdf escaneado asi que en el caso que no tenga 
        estos datos o no estes seguro si son correctos, rellena su espacio con un No Identificado. EN LA RESPUESTA NO INCLUYAS LOS PARENTESIS DESPUES DE CADA CATEGORIA.
        Cada campo debe estar separado por un enter. SI O SI TIENES QUE RESPONDER EN EL FOMATO QUE TE DI. TODAS LAS CATEGORIAS SI O SI TIENEN QUE ESTAR PRESENTES, si no
        estan presentes, rellena lo que sigue los : con un No Identificado. Ademas, las categorias deben permanecer exactamente con el mismo nombre. Deja las categorias en minuscula.""" + prompt,
        max_tokens=2000,
        temperature=0.01

        
    )
    return response.choices[0].text

def interact_with_gpt_2(prompt): #This can be modified to any prompt
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="""De este texto extrae los items de una compra. descripcion, cantidad, marca, unidad_monetaria (PESOS, DOLAR, EURO), valor,
        valor_subtotal, iva, aui (VALOR DE ADMINISTRACIÓN, IMPREVISTOS Y UTILIDAD), descuento (DESCUENTO EN VALORES NO PORCENTAJES), valor_total, 
        tiempo_garantia (TIEMPO EN MESES). Cabe destacar que esto es un documento pdf escaneado asi que en el caso que no tenga estos datos o no estes seguro si son correctos,
        rellena su espacio con un NA. A su vez, de manera logica deberas separar las palabras que no deben estar juntas. Cada campo debe estar separado por un enter tipo. SI O SI TIENES QUE RESPONDER EN 
        EL FOMATO QUE TE DI. EN LA RESPUESTA NO INCLUYAS LOS PARENTESIS QUE SE ENCUENTRAN DESPUES DEL NOMBRE DE CADA CATEGORIA. LAS CATEGORIAS DEBEN ESTAR SI O SI EN MINUSCULA y deberas mantener
        el mismo orden den el que te di las categorias. Habran veces que seran mas de un articulo, entonces tienes que hacer una division con un enter entre articulos. Cada articulo debe estar dividido
        de uno con el otro entre parrafos. RECUERDA QUE PUEDEN SER VARIOS ARTICULOS. Usa este ejemplo de PLANTILLA: descripcion: "KJ306S000 KEYSTONEJACKSTEREO3.5mmBLANCO", cantidad: "1", marca: "NA", 
        unidad_monetaria: "PESOS", valor: "10500", valor_subtotal: "10500", iva: "8246", aui: "NA", descuento: "NA", valor_total: "51646", tiempo_garantia: "3". Manten las categorias en minusucula.
        """ + prompt,
        max_tokens=2000,
        temperature=0.01
    )
    return response.choices[0].text




if __name__ == '__main__':
    app.run(debug=True)
