# OCR PDF Text Extraction API Using AI

Welcome to the PDF Text Extraction API. This API allows you to extract text and process information from PDF documents using various AI models from Open AI API using OCR. 

**NOTE: THIS WAS CREATED BEFORE OPEN AI API RELEASED FUNCTIONS. THIS ONLY USES PROMPTS TO EXTRACT INFORMATION, BUT YOU CAN MAKE PR TO ADD GPT FUNCTIONS.**

## Usage

### Endpoint

The API endpoint for processing PDF files is:


#### POST /process

### Request

The endpoint expects a POST request with a PDF file as a form data parameter named `pdfFile`. Additionally, you need to include an API key in the request headers as `X-Api-Key`.

### Example Request

```http
POST /process
Content-Type: multipart/form-data
X-Api-Key: YOUR_API_KEY_HERE

[PDF FILE CONTENT]

```

### Response

The API response will contain a JSON object with the extracted information from the PDF file. The response includes both categorized data and extracted articles.

Example Response

```
{
  "": {
    "identificacion_proveedor": "123456789",
    "nombre_proveedor": "John Doe",
    "correo_proveedor": "john@example.com",
    "contacto_proveedor": "John Doe",
    "direccion_proveedor": "123 Main St",
    "telefono_proveedor": "555-1234",
    "codigo_cotizacion_proveedor": "CQ123456",
    "tiempo_vigencia": "30",
    "forma_pago": "Contado",
    "metodo_pago": "Transferencia Bancaria",
    "condicion_pago": "60% Anticipo, 40% Contraentrega",
    "condiciones_entrega": "Instalado",
    "tiempo_entrega": "7",
    "costo_transporte": "100",
    "direccion_web": "example.com"
  },
  "articulos": [
    {
      "descripcion": "Product 1",
      "cantidad": "2",
      "marca": "Brand 1",
      "unidad_monetaria": "PESOS",
      "valor": "100",
      "valor_subtotal": "200",
      "iva": "16",
      "aui": "NA",
      "descuento": "NA",
      "valor_total": "216",
      "tiempo_garantia": "12"
    },
    {
      "descripcion": "Product 2",
      "cantidad": "1",
      "marca": "Brand 2",
      "unidad_monetaria": "DOLAR",
      "valor": "50",
      "valor_subtotal": "50",
      "iva": "8",
      "aui": "NA",
      "descuento": "NA",
      "valor_total": "58",
      "tiempo_garantia": "6"
    }
  ]
}
```

Example POST Request
Here's an example of how to make a POST request to the API using Python's requests library:

```
import requests

url = 'http://localhost:5000/process'
files = {'pdfFile': open('example.pdf', 'rb')}
headers = {'X-Api-Key': 'YOUR_API_KEY_HERE'}

response = requests.post(url, files=files, headers=headers)
print(response.json())

```

## Feedback

Feel free to improve OCR or AI integration by making a PR. Issues will also be addressed in this same repository.

