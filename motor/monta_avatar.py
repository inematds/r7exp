#!/usr/bin/env python3
"""Junta as falas do avatar de uma versão num só vídeo e transcreve cada fala (tempo por palavra).

Uso: motor/monta_avatar.py <pasta-do-completo> <versao>
Ordem: abertura da versão → caminhos (na ordem da ficha) → final. Cada fala: loudnorm -14 LUFS + 0,5 s de respiro.
Saída: build/avatar-<v>.mp4, build/segmentos-<v>.json, tempos/<fala>.json (whisper large-v3 do inemavox, uma vez por fala).
"""
import json, subprocess, sys
from pathlib import Path
import yaml

VOX = Path.home() / "projetos/inemavox"
PY = VOX / "venv/bin/python"
RESPIRO = 0.5


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).strip())


def tempos(pasta, fala):
    out = pasta / "tempos" / f"{fala}.json"
    if out.exists():
        return
    tmp = pasta / "tempos" / f"_{fala}"
    tmp.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(PY), str(VOX / "transcrever_v1.py"), "--in", str(pasta / "avatar" / f"{fala}.mp4"), "--outdir", str(tmp),
                    "--whisper-model", "large-v3", "--src", "pt", "--words"], check=True, stdout=subprocess.DEVNULL, timeout=1800)
    out.write_text((tmp / "words.json").read_text())


def main():
    pasta, v = Path(sys.argv[1]).resolve(), sys.argv[2]
    f = yaml.safe_load((pasta / "ficha.yaml").read_text())
    ordem = [f["aberturas"][v]["fala"]] + [c["fala"] for c in f["caminhos"]] + [f["final"]["fala"]]
    b = pasta / "build"; b.mkdir(exist_ok=True)
    segs, t = [], 0.0
    partes = []
    for fala in ordem:
        mp4 = pasta / "avatar" / f"{fala}.mp4"
        if not mp4.exists():
            raise SystemExit(f"falta o avatar {mp4}")
        tempos(pasta, fala)
        norm = b / f"n-{fala}.mp4"
        if not norm.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"fps=30,scale=1920:1080,setsar=1,tpad=stop_mode=clone:stop_duration={RESPIRO}",
                            "-af", f"aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,apad=pad_dur={RESPIRO}",
                            "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-shortest", str(norm)], check=True)
        d = dur(norm)
        segs.append({"fala": fala, "ini": round(t, 3), "dur": round(d, 3)})
        partes.append(norm); t += d
    lista = b / f"lista-{v}.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in partes))
    saida = b / f"avatar-{v}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", "-movflags", "+faststart", str(saida)], check=True)
    total = dur(saida)
    (b / f"segmentos-{v}.json").write_text(json.dumps({"segmentos": segs, "total": round(total, 3)}, indent=1))
    print(f"ok {saida} · {total:.1f} s · {len(segs)} falas")


if __name__ == "__main__":
    main()
