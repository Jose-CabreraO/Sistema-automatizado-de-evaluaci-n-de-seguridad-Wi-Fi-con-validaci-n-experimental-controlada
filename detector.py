def buscar_evil_twin(lista_redes):
    alertas = []
    ssids = [r['nombre'] for r in lista_redes]
    duplicados = set([x for x in ssids if ssids.count(x) > 1])
    
    for nombre in duplicados:
        redes = [r for r in lista_redes if r['nombre'] == nombre]
        # Si una es segura y otra es Open, hay sospecha
        tiene_open = any(r['auth'] in ['Open', 'Abierta'] for r in redes)
        if tiene_open:
            alertas.append(nombre)
    return alertas