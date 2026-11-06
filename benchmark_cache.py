import time
import statistics
from app import app
from cache_manager import cache

def ejecutar_benchmark(num_repeticiones=50):
    client = app.test_client()
    url = "/api/libros"

    print("=" * 70)
    print(" BENCHMARK DE RENDIMIENTO: API REST BIBLIOTECA UNIVERSITARIA")
    print(f" Endpoint evaluado: GET {url}")
    print(f" Numero de iteraciones por prueba: {num_repeticiones}")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. PRUEBA SIN CACHE (Consultas directas a la Base de Datos)
    # -------------------------------------------------------------
    cache.enabled = False
    tiempos_sin_cache = []

    for _ in range(num_repeticiones):
        t0 = time.perf_counter()
        res = client.get(url)
        t1 = time.perf_counter()
        assert res.status_code == 200
        tiempos_sin_cache.append((t1 - t0) * 1000)  # Convertir a ms

    media_sin_cache = statistics.mean(tiempos_sin_cache)
    p50_sin_cache = statistics.median(tiempos_sin_cache)
    p95_sin_cache = statistics.quantiles(tiempos_sin_cache, n=20)[18] if len(tiempos_sin_cache) >= 20 else max(tiempos_sin_cache)

    # -------------------------------------------------------------
    # 2. PRUEBA CON CACHE (Cache-Aside activado en memoria)
    # -------------------------------------------------------------
    cache.clear()
    cache.enabled = True
    tiempos_con_cache = []
    hits = 0
    misses = 0

    for _ in range(num_repeticiones):
        t0 = time.perf_counter()
        res = client.get(url)
        t1 = time.perf_counter()
        assert res.status_code == 200
        if res.headers.get("X-Cache") == "HIT":
            hits += 1
        else:
            misses += 1
        tiempos_con_cache.append((t1 - t0) * 1000)  # Convertir a ms

    media_con_cache = statistics.mean(tiempos_con_cache)
    p50_con_cache = statistics.median(tiempos_con_cache)
    p95_con_cache = statistics.quantiles(tiempos_con_cache, n=20)[18] if len(tiempos_con_cache) >= 20 else max(tiempos_con_cache)

    # Solo las peticiones que fueron efectivamente HIT
    tiempos_solo_hits = tiempos_con_cache[1:] if len(tiempos_con_cache) > 1 else tiempos_con_cache
    media_hits = statistics.mean(tiempos_solo_hits)

    # -------------------------------------------------------------
    # 3. CALCULO DE REDUCCION PORCENTUAL (Formula Seccion 12.2)
    # Reduccion (%) = ((Tiempo sin cache - Tiempo con cache) / Tiempo sin cache) * 100
    # -------------------------------------------------------------
    reduccion_pct = ((media_sin_cache - media_con_cache) / media_sin_cache) * 100
    reduccion_hits_pct = ((media_sin_cache - media_hits) / media_sin_cache) * 100
    tasa_aciertos = (hits / num_repeticiones) * 100

    print("\n--- RESULTADOS COMPARATIVOS ---")
    print(f"{'Metrica':<35} | {'Sin Cache (BD)':<15} | {'Con Cache (RAM)':<15}")
    print("-" * 70)
    print(f"{'Tiempo promedio de respuesta (ms)':<35} | {media_sin_cache:>12.2f} ms | {media_con_cache:>12.2f} ms")
    print(f"{'Mediana / Percentil 50 (p50)':<35} | {p50_sin_cache:>12.2f} ms | {p50_con_cache:>12.2f} ms")
    print(f"{'Latencia Percentil 95 (p95)':<35} | {p95_sin_cache:>12.2f} ms | {p95_con_cache:>12.2f} ms")
    print(f"{'Tiempo promedio solo en HIT (ms)':<35} | {'N/A':>15} | {media_hits:>12.2f} ms")
    print(f"{'Tasa de aciertos (Hit Rate %)':<35} | {'0.00 %':>15} | {tasa_aciertos:>12.2f} %")
    print(f"{'Aciertos (HIT) / Fallos (MISS)':<35} | {'0 / ' + str(num_repeticiones):>15} | {f'{hits} / {misses}':>15}")
    print("=" * 70)
    print(f"\n>>> REDUCCION GENERAL DEL TIEMPO DE RESPUESTA: {reduccion_pct:.2f} %")
    print(f">>> REDUCCION EN CONSULTAS EN CACHE (HIT):      {reduccion_hits_pct:.2f} %")
    print("=" * 70)

    stats = cache.get_stats()
    print("\nEstado final del Cache:")
    print(f" - Entradas activas: {stats['entradas_activas']}")
    print(f" - Claves: {stats['claves_almacenadas']}")


if __name__ == "__main__":
    ejecutar_benchmark(50)
