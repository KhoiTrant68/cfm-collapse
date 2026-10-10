"""A stand-in for nvidia-smi when NVML is unusable (driver/library version mismatch).

nvidia-smi, nvitop and gpustat all go through NVML, so they fail together when the
user-space NVML library and the loaded kernel module disagree. The CUDA driver API
still works, so this reports what it can see through it:

    per GPU   name, memory used / total (device-wide, all users)
    per GPU   the processes that hold /dev/nvidia<N> open (only those this user may
              inspect), with user, elapsed time and command

It cannot report utilisation, temperature, power or per-process memory: those exist
only through NVML. Each run creates a short-lived CUDA context on every GPU, so the
"used" figure includes a few hundred MB of its own while it measures.

    python scripts/gpu_status.py            # once
    watch -n 10 python scripts/gpu_status.py
"""
from __future__ import annotations

import os
import pwd
import time
import warnings


def gpu_processes() -> dict[int, list[tuple[int, str, str, str]]]:
    """pid, user, elapsed, command for every visible process holding /dev/nvidia<N>."""
    out: dict[int, list] = {}
    me = os.getpid()
    boot = time.time() - float(open("/proc/uptime").read().split()[0])
    hz = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    for pid in filter(str.isdigit, os.listdir("/proc")):
        if int(pid) == me:
            continue
        try:
            fds = os.listdir(f"/proc/{pid}/fd")
        except (PermissionError, FileNotFoundError):
            continue
        devs = set()
        for fd in fds:
            try:
                target = os.readlink(f"/proc/{pid}/fd/{fd}")
            except OSError:
                continue
            if target.startswith("/dev/nvidia") and target[11:].isdigit():
                devs.add(int(target[11:]))
        if not devs:
            continue
        try:
            st = os.stat(f"/proc/{pid}")
            user = pwd.getpwuid(st.st_uid).pw_name
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
            start = int(open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()[19]) / hz
            el = int(time.time() - boot - start)
        except (OSError, ValueError, KeyError):
            continue
        elapsed = f"{el // 3600}:{el % 3600 // 60:02d}:{el % 60:02d}"
        for d in devs:
            out.setdefault(d, []).append((int(pid), user, elapsed, " ".join(cmd.split())[:80]))
    return out


def main() -> None:
    warnings.filterwarnings("ignore")
    import torch

    procs = gpu_processes()
    print(time.strftime("%Y-%m-%d %H:%M:%S"), "(memory via CUDA; utilisation unavailable without NVML)")
    for i in range(torch.cuda.device_count()):
        free, total = torch.cuda.mem_get_info(i)
        used = total - free
        bar = "#" * round(20 * used / total)
        print(f"\nGPU {i}  {torch.cuda.get_device_name(i)}  "
              f"{used / 2**30:5.1f} / {total / 2**30:.1f} GB  [{bar:<20s}]")
        for pid, user, el, cmd in sorted(procs.get(i, [])):
            print(f"   pid {pid:<8d} {user:<10s} {el:>9s}  {cmd}")
        if not procs.get(i):
            print("   (no process visible to this user)")


if __name__ == "__main__":
    main()
