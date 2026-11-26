
#!/bin/bash

DEST="/home/embebidos/mame/roms"
SCRIPT="/home/embebidos/scripts/sync_usb_roms.py"
REPORT="/tmp/roms_importadas.txt"
LOG="/home/embebidos/logs/usb_watcher.log"

mkdir -p "$(dirname "$LOG")"

EXIT_FLAG="/tmp/usb_watcher_exit"
PAUSE_FLAG="/tmp/usb_watcher_pause"
MENU_FLAG="/tmp/usb_watcher_menu"
CHOICE_FLAG="/tmp/usb_watcher_choice"

LAST_DEV=""

find_usb_part() {
	lsblk -nrpo NAME,TYPE,TRAN |
	awk '$2=="disk" && $3=="usb" {print $1; exit}' |
	while read -r disk; do
		lsblk -nrpo NAME,TYPE "$disk" |
		awk '$2=="part" {print $1; exit}'
	done
}

get_mame_pid() {
	pgrep -x mame | tail -n 1
}

while true; do
	[ -f "$EXIT_FLAG" ] && exit 0
	DEV=$(find_usb_part 2>/dev/null || true)
	if [ -n "$DEV" ] && [ -b "$DEV" ]; then
		if [ "$DEV" != "$LAST_DEV" ]; then
			LAST_DEV="$DEV"
			echo "USB detectada: $DEV" >> "$LOG"
			touch "$PAUSE_FLAG"
			MAME_PID=""
			for _ in {1..60}; do
				MAME_PID=$(get_mame_pid || true)
				[ -n "$MAME_PID" ] && break
				sleep 0.25
			done

			if [ -n "$MAME_PID" ]; then
				kill -TERM "$MAME_PID" 2>/dev/null
				for _ in {1..20}; do
                			kill -0 "$MAME_PID" 2>/dev/null
					sleep 0.25
				done
				kill -0 "$MAME_PID" 2>/dev/null && kill -KILL "$MAME_PID" 2>/dev/null
			fi
			echo "=========================" >> "$LOG"
			echo "  MEMORIA USB DETECTADA: $DEV" >> "$LOG"

			if udisksctl mount -b "$DEV" >> "$LOG" 2>&1; then
				MNT=$(lsblk -nrpo MOUNTPOINT "$DEV" | head -n 1)
				if [ -n "$MNT" ] && [ -d "$MNT" ]; then
					rm -f "$REPORT"
					echo "Iniciando deteccion e importacion de ROMs desde $MNT..." >> "$LOG"
					python3 "$SCRIPT" "$MNT" "$DEST" "$REPORT" >> "$LOG" 2>&1 || true
					udisksctl unmount -b "$DEV" >> "$LOG" 2>&1 || true
				else
					echo "ERROR: No se encontro la ruta de montaje." >> "$LOG"
					echo "No se pudo acceder a la memoria USB." > "$REPORT"
					udisksctl unmount -b "$DEV" >> "$LOG" 2>&1 || true
				fi
			else
				echo "ERROR: No se pudo montar la memoria USB." >> "$LOG"
				echo "Error al montar la memoria USB." > "$REPORT"
			fi

			rm -f "$CHOICE_FLAG"
			touch "$MENU_FLAG"

			while [ ! -f "$CHOICE_FLAG" ]; do
				[ -f "$EXIT_FLAG" ] && exit 0
				sleep 0.5
			done

			OPTION=$(cat "$CHOICE_FLAG")
			rm -f "$CHOICE_FLAG" "$MENU_FLAG"

			if [ "$OPTION" = "1" ]; then
				echo
				echo "Reanudando MAME..." >> "$LOG"
				rm -f "$PAUSE_FLAG"
			elif [ "$OPTION" = "2" ]; then
				echo
				echo "Regresando al menu de titulos..." >> "$LOG"
				touch "$EXIT_FLAG"
				rm -f "$PAUSE_FLAG"
				exit 0
			else
				echo "Opcion no valida." >> "$LOG"
				rm -f "$PAUSE_FLAG"
			fi
		fi
	else
		LAST_DEV=""
	fi
	sleep  1
done

