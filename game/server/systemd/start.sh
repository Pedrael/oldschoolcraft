#!/usr/bin/env bash
# OldSchoolCraft 1.7.10 Forge — Linux launcher (replaces START-SERVER.bat).
# No restart loop here: systemd owns restarts (Restart=on-failure).
set -euo pipefail
cd "$(dirname "$0")"

FORGE_JAR="forge-1.7.10-10.13.4.1614-1.7.10-universal.jar"
[[ -f "$FORGE_JAR" ]] || { echo "[X] $FORGE_JAR missing. Wrong directory?" >&2; exit 1; }

JAVA_EXE="${JAVA_EXE:-/opt/java/temurin8/bin/java}"
[[ -x "$JAVA_EXE" ]] || { echo "[X] No Java 8 at $JAVA_EXE" >&2; exit 1; }
if ! "$JAVA_EXE" -version 2>&1 | grep -q '"1\.8'; then
  echo "[X] $JAVA_EXE is not Java 8 — 1.7.10 will not run:" >&2
  "$JAVA_EXE" -version >&2; exit 1
fi
echo "Using Java: $JAVA_EXE"; "$JAVA_EXE" -version 2>&1 | head -1

# Ryzen 5 5600G, 6C/12T, 30 GB RAM. Heap matches the old Windows box.
HEAP="${HEAP:-8G}"

JVM_ARGS=(
  -Xms"$HEAP" -Xmx"$HEAP"
  -XX:+UseG1GC -XX:+UnlockExperimentalVMOptions
  -XX:+ParallelRefProcEnabled -XX:+DisableExplicitGC -XX:+AlwaysPreTouch
  -XX:MaxGCPauseMillis=200 -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40
  -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5
  -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15
  -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5
  -XX:SurvivorRatio=32 -XX:MaxTenuringThreshold=1 -XX:+PerfDisableSharedMem
  -XX:ParallelGCThreads=6 -XX:ConcGCThreads=2 -XX:MetaspaceSize=256M
  # 129 mods take a while to sync on join — stop FML timing players out
  -Dfml.readTimeout=180 -Dfml.loginTimeout=1200
  -Djava.awt.headless=true
)

# one-shot FML missing-mapping auto-confirm — same contract as START-SERVER.bat
if [[ -f fml-confirm-once.flag ]]; then
  JVM_ARGS+=(-Dfml.queryResult=confirm)
  rm -f fml-confirm-once.flag
fi

# exec keeps this PID, so the pidfile points at the JVM and systemd can see crashes
[[ -d /run/minecraft ]] && echo $$ > /run/minecraft/minecraft.pid

echo "Starting OldSchoolCraft — heap ${HEAP}. Type 'stop' for a clean shutdown."
exec "$JAVA_EXE" "${JVM_ARGS[@]}" -jar "$FORGE_JAR" nogui
