"""
profiling_examples.py
---------------------
Conjunt d'exemples de programació defensiva, temporització i profiling.
Cada snippet està encapsulat en una funció perquè es pugui cridar de forma independent.

Ús bàsic des de línia de comandes:
    python profiling_examples.py --func <nom_funcio>

Funcions disponibles:
    - assertion_example
    - timing_example
    - cprofile_example
    - tracemalloc_example
    - memory_profiler_example
    - psutil_rss_example
"""

from __future__ import annotations


def assertion_example() -> None:
    """Exemple d'ús d'assertions dins d'un bucle.

    El codi s'atura quan troba un valor no positiu i llança un AssertionError.
    """
    numbers = [1.5, 2.3, 0.7, -0.001, 4.4]
    total = 0.0
    for n in numbers:
        assert n >= 0.0, 'Les dades han de contenir només valors positius'
        total += n
    print('total és:', total)


def timing_example() -> None:
    """Mesura simple del temps d'execució d'una funció amb perf_counter."""
    import time

    def work_timing():
        # Treball artificial per tenir una mica de càrrega
        return sum(i * i for i in range(1_00_000))

    t0 = time.perf_counter()
    work_timing()
    t1 = time.perf_counter()
    print(f"Temps: {t1 - t0:.6f} s")


def cprofile_example() -> None:
    """Exemple d'ús de cProfile + pstats i ordenació per 'cumtime'."""
    import cProfile
    import pstats

    def work_profile():
        # Treball artificial
        return sum(i * i for i in range(1_00_000))

    with cProfile.Profile() as pr:
        work_profile()

    stats = pstats.Stats(pr).strip_dirs().sort_stats("cumtime")
    stats.print_stats(10)  # top 10 entrades


def tracemalloc_example() -> None:
    """Exemple d'ús de tracemalloc per detectar hotspots i regressions de memòria."""
    import tracemalloc

    def allocate_data():
        # Reserva memòria: llistes i dicts de mida moderada
        data = [i for i in range(300_000)]
        mapping = {i: i * 2 for i in range(150_000)}
        # Evitem que l'optimitzador elimini les variables
        return len(data) + len(mapping)

    tracemalloc.start()
    snap1 = tracemalloc.take_snapshot()

    allocate_data()

    snap2 = tracemalloc.take_snapshot()

    print("TOP línies per bytes (snapshot 2):")
    for stat in snap2.statistics("lineno")[:10]:
        print(stat)

    print("\nDiferències (snap2 - snap1):")
    for stat in snap2.compare_to(snap1, "lineno")[:10]:
        print(stat)


def memory_profiler_example() -> None:
    """Exemple línia a línia amb memory_profiler.

    Per obtenir el perfil línia a línia, cal executar amb:
        python -m memory_profiler profiling_examples.py --func memory_profiler_example
    Si la llibreria no està instal·lada, es mostrarà un missatge.
    """
    try:
        from memory_profiler import profile
    except Exception as e:
        print("⚠️  memory_profiler no està disponible:", e)
        print("Instal·la-la amb: pip install memory_profiler")
        return

    @profile
    def work():
        # Operacions que creen i processen dades
        data = [i for i in range(500_000)]
        doubled = [x * 2 for x in data]
        return sum(doubled)

    # Executem la funció perfilada
    result = work()
    print("Resultat:", result)


def memory_profiler_eficient_example() -> None:
    """Versió més eficient en memòria: un sol bucle, sense llistes temporals.

    Implementa la feina en un sol bucle per evitar llistes intermitges i reduir ús de memòria.
    Es pot perfil·lar amb memory_profiler si està instal·lada.
    """
    try:
        from memory_profiler import profile  # type: ignore
    except Exception:
        # Decorador no-op si memory_profiler no està disponible
        def profile(func):
            return func

    @profile
    def work():
        total = 0
        for i in range(500_000):
            total += i * 2
        return total

    result = work()
    print("Resultat (single-loop):", result)


def psutil_rss_example() -> None:
    """Monitorització del RSS del procés amb psutil."""
    try:
        import psutil
    except Exception as e:
        print("⚠️  psutil no està disponible:", e)
        print("Instal·la-la amb: pip install psutil")
        return

    import os
    import time

    proc = psutil.Process(os.getpid())

    def rss_mb() -> float:
        return proc.memory_info().rss / (1024 * 1024)

    print(f"RSS inicial: {rss_mb():.1f} MB")
    # Simulem activitat que pot incrementar la memòria
    data = [i for i in range(300_000)]
    time.sleep(0.3)
    print(f"RSS després d'allocar: {rss_mb():.1f} MB")
    # Alliberem referència i deixem que el GC actuï
    del data
    time.sleep(0.3)
    print(f"RSS final: {rss_mb():.1f} MB")


def _list_functions() -> None:
    fns = [
        "assertion_example",
        "timing_example",
        "cprofile_example",
        "tracemalloc_example",
        "memory_profiler_example",
        "memory_profiler_eficient_example",
        "psutil_rss_example",
    ]
    print("Funcions disponibles:")
    for name in fns:
        print("  -", name)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Executa exemples de temporització i profiling.")
    parser.add_argument("--func", type=str, help="Nom de la funció a executar")
    args = parser.parse_args()

    if not args.func:
        _list_functions()
    else:
        # Executa la funció demanada si existeix
        fn = globals().get(args.func)
        if callable(fn):
            fn()
        else:
            print(f"Funció no trobada: {args.func}\n")
            _list_functions()
