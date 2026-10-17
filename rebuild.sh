#!/bin/sh
# Rebuild image TANPA cache lalu restart container.
#
#   ./rebuild.sh            rebuild no-cache + restart (data MySQL aman)
#   ./rebuild.sh --fresh    sama, tapi HAPUS volume MySQL
#   ./rebuild.sh --prune    sama, tapi bersihkan juga build cache Docker
#   ./rebuild.sh --no-logs  tidak menampilkan log di akhir
set -e
cd "$(dirname "$0")"

FRESH=0; PRUNE=0; LOGS=1
for arg in "$@"; do
  case "$arg" in
    --fresh) FRESH=1 ;;
    --prune) PRUNE=1 ;;
    --no-logs) LOGS=0 ;;
    *) echo "Opsi tidak dikenal: $arg"; exit 1 ;;
  esac
done

if [ "$FRESH" = 1 ]; then
  printf "PERINGATAN: volume MySQL akan DIHAPUS. Lanjut? (y/N) "
  read -r ans
  [ "$ans" = "y" ] || { echo "Dibatalkan."; exit 0; }
  docker compose down --volumes --remove-orphans
else
  docker compose down --remove-orphans
fi

[ "$PRUNE" = 1 ] && docker builder prune -f

docker compose build --no-cache --pull
docker compose up -d --force-recreate --renew-anon-volumes
docker compose ps

[ "$LOGS" = 1 ] && docker compose logs -f web
exit 0
