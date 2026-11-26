import os
import subprocess
import sys
import pygame

ROMS_DIR = "/home/embebidos/roms"
MAME_DIR = "/home/embebidos"
IMPORT_LIST = "/tmp/roms_importadas.txt"

def get_roms():
    if not os.path.isdir(ROMS_DIR):
        return []
    return sorted([f for f in os.listdir(ROMS_DIR) if f.lower().endswith(".zip")])

def get_imported_banner():
    if os.path.isfile(IMPORT_LIST) and os.path.getsize(IMPORT_LIST) > 0:
        with open(IMPORT_LIST, "r", encoding="utf-8", errors="ignore") as f:
            items = [line.strip() for line in f if line.strip()]
        if items:
            return f"Nuevas ROMs importadas: {', '.join(items[:3])}"
    return ""

def launch_mame(rom_filename):
    rom_name = os.path.splitext(rom_filename)[0]
    pygame.quit()
    subprocess.run(
        ["./mame", rom_name, "-video", "soft"],
        cwd=MAME_DIR,
        check=False,
    )

def main():
    while True:
        pygame.init()
        info = pygame.display.Info()
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
        pygame.display.set_caption("Consola MAME")
        clock = pygame.time.Clock()
        font_title = pygame.font.SysFont(None, 48)
        font_item = pygame.font.SysFont(None, 36)
        font_small = pygame.font.SysFont(None, 24)

        roms = get_roms()
        selected = 0
        running_menu = True
        launched_rom = None

        while running_menu:
            roms = get_roms()
            if roms and selected >= len(roms):
                selected = len(roms) - 1
            banner = get_imported_banner()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN and roms:
                        selected = (selected + 1) % len(roms)
                    elif event.key == pygame.K_UP and roms:
                        selected = (selected - 1) % len(roms)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and roms:
                        launched_rom = roms[selected]
                        running_menu = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)

            screen.fill((18, 22, 34))
            title_surf = font_title.render("MENÚ DE TÍTULOS", True, (255, 215, 0))
            screen.blit(title_surf, (40, 30))

            if banner:
                b_surf = font_small.render(banner, True, (120, 255, 160))
                screen.blit(b_surf, (40, 82))

            if not roms:
                empty_surf = font_item.render("No hay ROMs (.zip) en /home/embebidos/roms", True, (240, 110, 110))
                screen.blit(empty_surf, (40, 140))
            else:
                start_idx = max(0, selected - 6)
                visible = roms[start_idx:start_idx + 12]
                for idx, rom in enumerate(visible):
                    real_idx = start_idx + idx
                    y = 130 + idx * 42
                    is_sel = real_idx == selected
                    color = (255, 255, 255) if is_sel else (175, 185, 205)
                    prefix = "> " if is_sel else "  "
                    surf = font_item.render(f"{prefix}{rom}", True, color)
                    screen.blit(surf, (50, y))

            help_surf = font_small.render("Flechas: Mover | Enter: Jugar | Esc: Salir", True, (150, 160, 180))
            screen.blit(help_surf, (40, info.current_h - 45))

            pygame.display.flip()
            clock.tick(30)

        if launched_rom:
            launch_mame(launched_rom)

if __name__ == "__main__":
    main()
