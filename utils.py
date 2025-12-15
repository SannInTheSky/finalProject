# utils.py
import json
from dicttoxml import dicttoxml
from flask import Response

def json_to_xml(data, root_name='response'):
    """
    Convert JSON data to XML format
    """
    try:
        # If data is a list, wrap it
        if isinstance(data, list):
            data = {root_name: data}
        
        # Convert to XML
        xml_data = dicttoxml(data, custom_root=root_name, attr_type=False)
        return xml_data.decode('utf-8')
    except Exception as e:
        # Fallback to simple XML conversion
        return f'<error>Failed to convert to XML: {str(e)}</error>'

def format_response(data, format_type='json'):
    """
    Format response based on requested format
    """
    if format_type == 'xml':
        xml_data = json_to_xml(data)
        return Response(xml_data, mimetype='application/xml')
    else:
        return jsonify(data)