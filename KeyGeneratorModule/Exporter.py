import json
import base64
import os


class Exporter:

    # Verifica si una ruta existe, y en caso de no existir trata de crearla; retorna un valor boleano
    @staticmethod
    def verify_path(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                print(f'Ruta {path} creada exitosamente')
                return True
            except OSError as e:
                print(f'Error al crear la ruta "{path}": {e}')
                return False
        else:
            print(f'Ruta {path} ya existe')
            return True

    @staticmethod
    def dictionary_to_json(dictionary):
        return json.dumps(dictionary)

    @staticmethod
    def json_to_bytes(json_s):
        return json_s.encode('utf-8')

    @staticmethod
    def bytes_to_b64(string):
        return base64.b64encode(string)

    @staticmethod
    def b64_to_bytes(b64_s):
        return base64.b64decode(b64_s)

    @staticmethod
    def bytes_to_json(bytes_s):
        return bytes_s.decode('utf-8')

    @staticmethod
    def json_to_dictionary(bytes_s):
        return json.loads(bytes_s)

    @staticmethod
    def b64_to_pem_file(b64_s, file_name, path):
        file_path = os.path.join(path, f'{file_name}.pem')
        with open(file_path, "wb") as file:
            file.write(b64_s)

    @staticmethod
    def pem_file_to_b64(path):
        with open(path, 'r') as archivo:
            b64_s = archivo.read()
            return b64_s.encode('utf-8')

    @staticmethod
    def export_key(dict_key, path, key_name):
        key = Exporter.dictionary_to_json(dict_key)
        key = Exporter.json_to_bytes(key)
        key = Exporter.bytes_to_b64(key)
        Exporter.b64_to_pem_file(key, key_name, path)

    @staticmethod
    def import_key(path):
        try:
            data = Exporter.pem_file_to_b64(path)
            data = Exporter.b64_to_bytes(data)
            data = Exporter.bytes_to_json(data)
            data = Exporter.json_to_dictionary(data)
            return data
        except Exception as e:
            raise

    @staticmethod
    def make_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)
            return path
        else:
            return path

    @staticmethod
    def int_to_base64(*integers):
        if len(integers) == 1:
            integer = integers[0]
            integer_bytes_array = integer.to_bytes((integer.bit_length() + 7) // 8, 'big')
            b64 = base64.b64encode(integer_bytes_array).decode('utf-8')
            return b64
        else:
            strings_base64 = []
            for integer in integers:
                integer_bytes_array = integer.to_bytes((integer.bit_length() + 7) // 8, 'big')
                b64 = base64.b64encode(integer_bytes_array).decode('utf-8')
                strings_base64.append(b64)
        return tuple(strings_base64)

    @staticmethod
    def base64_to_int(*strings_base64):
        if len(strings_base64) == 1:
            b64 = strings_base64[0]
            bytes_b64 = base64.b64decode(b64)
            integer = int.from_bytes(bytes_b64, 'big')
            return integer
        else:
            integers = []
            for b64 in strings_base64:
                bytes_b64 = base64.b64decode(b64)
                integer = int.from_bytes(bytes_b64, 'big')
                integers.append(integer)
            return tuple(integers)
