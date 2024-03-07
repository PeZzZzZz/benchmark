# -*- coding: utf-8 -*-
import argparse
import os
import socket
import threading
import time
import urllib.request

COLOR_LIGHT_RED="\033[1;31m"
COLOR_LIGHT_GREEN="\033[1;32m"
COLOR_LIGHT_BLUE="\033[1;34m"
COLOR_YELLOW="\033[1;33m"
COLOR_LIGHT_PURPLE = "\033[1;35m"
END = "\033[0m"



class Benchmark:

    def __init__(self, duration):
        self.duration = duration
        self.url = "http://ping.online.net/50Mo.dat"
        self.server_ip = 'nyc.speedtest.clouvider.net'
        self.server_port = 5201

    def ram_benchmark(self):
        print("Début du test de RAM")
        start_time = time.time()
        allocated_memory = []
        iteration = 0
        while time.time() - start_time < self.duration * 60:
            allocated_memory.append([0] * 100000)
            iteration += 1
            if iteration % 100 == 0:
                print(f"{COLOR_LIGHT_RED}Iteration {iteration}: Mémoire allouéjusqu'a present{END}")
        end_time = time.time()
        total_time = end_time - start_time
        average_allocated = sum(len(block) * 8 for block in allocated_memory) / len(allocated_memory)
        print(f"Test RAM terminé après {total_time:.2f} secondes.")
        print(f"Moyenne de mémoire allouée par itération: {average_allocated / (1024 ** 2):.2f} Mo")

    def cpu_benchmark(self):
        print("Début du test de CPU")
        start_time = time.time()
        iterations = 0
        while time.time() - start_time < self.duration * 60:
            [x ** 2 for x in range(100000)]
            iterations += 1
            if iterations % 10 == 0:
                print(f"{COLOR_LIGHT_GREEN}Iteration {iterations}: CPU utilise pour le calcul {END}")
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Test CPU terminé après {total_time:.2f} secondes.")

    def disk_benchmark(self):
        print("Début du test de disque")
        start_time = time.time()
        iterations = 0
        while time.time() - start_time < self.duration * 60:
            with open("test_file", "w") as f:
                f.write("0" * 10000000)
            os.remove("test_file")
            iterations += 1
            print(f"{COLOR_YELLOW}Iteration {iterations}: Fichier ecrit et suppr{END}")
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Test disque terminé après {total_time:.2f} secondes.")

    def download_test(self):
        start_time = time.time()
        total_download = 0
        while time.time() - start_time < self.duration * 60:
            start_download_time = time.time()
            with urllib.request.urlopen(self.url) as response:
                file = response.read()
                total_download += len(file)
            download_time = time.time() - start_download_time
            if download_time > 0:
                download_speed = len(file) / download_time / 1024 / 1024  # Vitesse en Mbps
                print(f"{COLOR_LIGHT_BLUE}{len(file)} octets téléchargés en {download_time:.2f} secondes à {download_speed:.2f} Mbps{END}")
        print(f"Test de téléchargement terminé, total téléchargé: {total_download / 1024 / 1024:.2f} MB")

    def netup_benchmark(self, buffer_size=1024):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((self.server_ip, self.server_port))
                data = b'0' * buffer_size
                start_time = time.time()
                total_bytes_sent = 0
                while time.time() - start_time < self.duration * 60:
                    sent = sock.send(data)
                    if sent == 0:
                        raise RuntimeError("Connexion rompue")
                    total_bytes_sent += sent
                    print(f"{COLOR_LIGHT_PURPLE}{sent} octets envoyés, total jusqua maintenant: maintenant: {total_bytes_sent} octets{END}")
                end_time = time.time()
                total_time = end_time - start_time
                throughput = (total_bytes_sent * 8) / (total_time * 1024 * 1024)  # Débit en Mbps
                print(f"Test terminé. Débit d'upload: {throughput:.2f} Mbps")
            except Exception as e:
                print(f"Erreur lors de la connexion ou du test: {e}")

    def run_benchmarks(self):
        if self.duration < 1:
            print("La durée doit être d'au moins 1 minute.")
            return

        threads = [
            threading.Thread(target=self.ram_benchmark),
            threading.Thread(target=self.cpu_benchmark),
            threading.Thread(target=self.disk_benchmark),
            threading.Thread(target=self.netup_benchmark),
            threading.Thread(target=self.download_test),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print("Tous les tests sont terminés.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark script pour RAM, CPU, Disk et Network")
    parser.add_argument("--download", action='store_true', help="Effectuer un test de téléchargement")
    parser.add_argument("--upload", action='store_true', help="Effectuer un test d'upload")
    parser.add_argument("--disk", action='store_true', help="Effectuer un test de disque")
    parser.add_argument("--cpu", action='store_true', help="Effectuer un test de CPU")
    parser.add_argument("--ram", action='store_true', help="Effectuer un test de RAM")
    parser.add_argument("--all", action='store_true', help="Effectuer tous les tests")
    parser.add_argument("--duration", type=int, default=1, help="Durée du test en minutes (minimum 1 minute)")
    args = parser.parse_args()

    benchmark = Benchmark(args.duration)

    if args.all:
        benchmark.run_benchmarks()
    elif args.download:
        benchmark.download_test()
    elif args.upload:
        benchmark.netup_benchmark()
    elif args.disk:
        benchmark.disk_benchmark()
    elif args.cpu:
        benchmark.cpu_benchmark()
    elif args.ram:
        benchmark.ram_benchmark()
    else:
        print("Aucun test sélectionné. Utilisez --all ou sélectionnez au moins un test individuel.")

