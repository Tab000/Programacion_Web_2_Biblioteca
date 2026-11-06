import yaml
import re

with open('openapi.yaml', 'r', encoding='utf-8') as f:
    spec = yaml.safe_load(f)

print('YAML Parsed successfully!')
paths = spec.get('paths', {})
print(f'Total paths: {len(paths)}')

total_ops = 0
for p, pdata in paths.items():
    for method, op in pdata.items():
        total_ops += 1
print(f'Total operations (endpoints HTTP): {total_ops}')

# Check 19 entities
targets = [
    ('Pais', '/api/paises', '/api/paises/{id_pais}'),
    ('Idioma', '/api/idiomas', '/api/idiomas/{id_idioma}'),
    ('Editorial', '/api/editoriales', '/api/editoriales/{id_editorial}'),
    ('Estado_Fisico', '/api/estados-fisicos', '/api/estados-fisicos/{id_estado_fisico}'),
    ('Facultad', '/api/facultades', '/api/facultades/{id_facultad}'),
    ('Tipo_Usuario', '/api/tipos-usuario', '/api/tipos-usuario/{id_tipo_usuario}'),
    ('Turno', '/api/turnos', '/api/turnos/{id_turno}'),
    ('Estado_Reserva', '/api/estados-reserva', '/api/estados-reserva/{id_estado_reserva}'),
    ('Estado_Prestamo', '/api/estados-prestamo', '/api/estados-prestamo/{id_estado_prestamo}'),
    ('Ciudad', '/api/ciudades', '/api/ciudades/{id_ciudad}'),
    ('Categoria', '/api/categorias', '/api/categorias/{id_categoria}'),
    ('Autor', '/api/autores', '/api/autores/{id_autor}'),
    ('Bibliotecario', '/api/bibliotecarios', '/api/bibliotecarios/{codigo_bibliotecario}'),
    ('Libro', '/api/libros', '/api/libros/{codigo_libro}'),
    ('Usuario', '/api/usuarios', '/api/usuarios/{codigo_usuario}'),
    ('Direccion', '/api/direcciones', '/api/direcciones/{id_direccion}'),
    ('Historial_Ubicacion', '/api/historial-ubicaciones', '/api/historial-ubicaciones/{id_historial}'),
    ('Reserva', '/api/reservas', '/api/reservas/{codigo_reserva}'),
    ('Prestamo', '/api/prestamos', '/api/prestamos/{id_prestamo}'),
]

all_ok = True
for name, c_url, i_url in targets:
    c_ops = list(paths.get(c_url, {}).keys())
    i_ops = list(paths.get(i_url, {}).keys())
    has_5 = ('get' in c_ops and 'post' in c_ops and 'get' in i_ops and 'put' in i_ops and 'delete' in i_ops)
    if not has_5:
        all_ok = False
        print(f'FAIL {name}: c={c_ops}, i={i_ops}')
    else:
        print(f'OK: {name} (5/5)')

print(f'All 19 entities covered: {all_ok}')

# Validate $ref integrity
content_str = yaml.dump(spec)
refs = re.findall(r'\$ref:\s*[\'"]?#/components/schemas/([^\s\'"]+)', content_str)
schemas = spec.get('components', {}).get('schemas', {})
broken = []
for r in set(refs):
    if r not in schemas:
        broken.append(r)
print(f'Total schemas: {len(schemas)}')
print(f'Broken refs: {broken}')
