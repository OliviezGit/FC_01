"""KiCad instance fields for the archived component catalogue."""

def local(path):
    return '${KIPRJMOD}/' + path

def fields(record, symbol_id):
    purchase = record['purchasing']
    supplier = purchase['supplier']
    confirmed = purchase['unit_eur_ht'] is not None and bool(purchase['order_code'])
    stock = purchase['stock']
    status = ('Offre France non confirmee' if not confirmed else
              'Stock non confirme' if stock is None else
              'Rupture au releve' if stock == 0 else 'Stock positif au releve')
    price = str(purchase['unit_eur_ht']) if confirmed else ''
    quantity = str(purchase['price_quantity']) if confirmed else ''
    digikey = supplier == 'DigiKey France' and confirmed
    return {
        'Component_Class': 'Composant achete',
        'Symbol_ID': symbol_id,
        'Symbol_Library_File': local(record['symbol_file']),
        'Footprint_File': local(record['footprint_file']),
        'Model_3D': local(record['model']['file']),
        'Model_3D_Type': record['model']['type'],
        'Component_PDF': local(record['control_pdf']),
        'Datasheet': local(record['datasheet_file']),
        'Datasheet_URL': record['datasheet_download_url'],
        'Supplier': supplier,
        'Supplier_Order_Code': purchase['order_code'],
        'Supplier_URL': purchase['url'],
        'Supplier_Status': status,
        'Supplier_Notes': purchase['notes'],
        'Unit_Price_EUR': price,
        'Price_Basis': 'EUR HT par piece, hors port' if confirmed else '',
        'Price_Qty': quantity,
        'Price_Checked': purchase['checked'],
        'Stock_Units': str(stock) if stock is not None else '',
        'Stock_Checked': purchase['checked'],
        # Keep existing export aliases consistent with the selected supplier.
        'DigiKey_Part_Number': purchase['order_code'] if digikey else '',
        'DigiKey_URL': purchase['url'] if digikey else '',
        'DigiKey Part Number': purchase['order_code'] if digikey else '',
        'DigiKey URL': purchase['url'] if digikey else '',
        'DigiKey Unit Price EUR': price if digikey else '',
        'DigiKey Price Qty': quantity if digikey else '',
        'DigiKey Status': status if digikey else 'Offre DigiKey France non retenue ou non confirmee',
        'Price Checked': purchase['checked'],
        'Footprint Audit': record['electrical_review']['review'],
        'Library Audit': 'Fichiers locaux; voir Component_PDF et verification/REPORT.md',
    }

def feature_fields(symbol_id, footprint_file):
    return {
        'Component_Class': 'Element fabrique dans le PCB; aucun composant achete',
        'Symbol_ID': symbol_id,
        'Symbol_Library_File': local('composants/kicad/FC01_Project.kicad_sym'),
        'Footprint_File': local(footprint_file),
        'Model_3D': '',
        'Model_3D_Type': 'Non applicable: cuivre, point test, cavalier ou trou du PCB',
        'Component_PDF': local('composants/controle/elements_PCB.pdf'),
        'Datasheet': '',
        'Datasheet_URL': '',
        'Supplier': 'Non applicable',
        'Supplier_Order_Code': '',
        'Supplier_URL': '',
        'Supplier_Status': 'Pas de composant a commander',
        'Supplier_Notes': 'Voir Component_PDF pour le symbole et le dessin de cuivre/perçage',
        'Unit_Price_EUR': '',
        'Price_Basis': '',
        'Price_Qty': '',
        'Price_Checked': '',
        'Stock_Units': '',
        'Stock_Checked': '',
        'DigiKey_Part_Number': '',
        'DigiKey_URL': '',
        'DigiKey Part Number': '',
        'DigiKey URL': '',
        'DigiKey Unit Price EUR': '',
        'DigiKey Price Qty': '',
        'DigiKey Status': 'Element PCB; aucun composant achete',
        'Price Checked': '',
    }
