# Anti-Virus 1.0 BETA

import os
import pygame
import threading
from concurrent.futures import ThreadPoolExecutor
import collections

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 900, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Anti-Virus 1.0 BETA")

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLACK = (0, 0, 0)

font = pygame.font.Font(None, 40)
small_font = pygame.font.Font(None, 24)

MALWARE_SIGNATURES = [
    b"malicious_file_signature_1",
    b"malicious_file_signature_2",
    b"fake_virus",
]

USER_DRIVE = os.path.abspath(os.sep)  # Will scan from root (C:/ or equivalent)


def get_all_files(root_dir):
    all_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            path = os.path.join(root, file)
            all_files.append(path)
    return all_files


def scan_file(file_path):
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            for sig in MALWARE_SIGNATURES:
                if sig in content:
                    return file_path, "infected"
    except Exception:
        return file_path, "error"
    return file_path, "clean"


def render_text(text, color, y):
    surf = small_font.render(text, True, color)
    screen.blit(surf, (20, y))


def start_scan():
    files = get_all_files(USER_DRIVE)
    total = len(files)
    scanned = 0
    infected_files = []
    error_files = []
    clean_files = []
    recent_scanned_files = collections.deque(maxlen=10)

    batch_size = 4
    with ThreadPoolExecutor(max_workers=batch_size) as executor:
        futures = []
        index = 0
        done = False

        while not done:
            while len(futures) < batch_size and index < total:
                path = files[index]
                futures.append(executor.submit(scan_file, path))
                index += 1

            done_futures = []
            for future in futures:
                if future.done():
                    file_path, status = future.result()
                    scanned += 1
                    recent_scanned_files.append(file_path)
                    if status == "infected":
                        infected_files.append(file_path)
                        print(f"\U0001F6D1 INFECTED: {file_path}")
                    elif status == "error":
                        error_files.append(file_path)
                        print(f"⚠️ ERROR reading: {file_path}")
                    else:
                        clean_files.append(file_path)
                        print(f"✅ Clean: {file_path}")
                    done_futures.append(future)

            futures = [f for f in futures if f not in done_futures]

            if index >= total and not futures:
                done = True

            screen.fill(WHITE)
            title = font.render("Anti-Virus 1.0 BETA", True, BLACK)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
            render_text(f"Scanned: {scanned} / {total}", BLACK, 60)
            render_text(f"Infected: {len(infected_files)}", RED, 90)
            render_text(f"Errors: {len(error_files)}", (200, 150, 0), 120)
            render_text(f"Clean: {len(clean_files)}", GREEN, 150)

            y_start = 180
            for i, fname in enumerate(list(recent_scanned_files)):
                display_name = fname[-80:] if len(fname) > 80 else fname
                render_text(f"→ {display_name}", BLACK, y_start + i * 20)

            pygame.display.flip()


scan_thread = threading.Thread(target=start_scan)
scan_thread.start()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.time.delay(100)

pygame.quit()
