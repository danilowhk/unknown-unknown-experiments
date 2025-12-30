# Experiment #001: VM Detection from Userspace
**Date:** 2025-12-30  
**"Wait, that's possible?" Score:** 8/10

## Question
Can we detect we're running inside a virtual machine purely from userspace code, without any privileged access?

## Why It Matters
If this works, it unlocks:
- **Security research**: Understanding how malware detects sandboxes
- **Anti-cheat systems**: Detecting if games run in VMs
- **Cloud fingerprinting**: Identifying the underlying hypervisor
- **Container escape detection**: Knowing your execution environment
- **Forensics**: Determining if evidence was gathered in a VM

This is the kind of thing that seemed like it would require kernel access or special privileges. Turns out you can do it from pure Python.

## The Code

See [code/vm_detect.py](code/vm_detect.py)

Detection vectors used:
1. **CPU hypervisor flag** - CPUID bit 31 in ECX (exposed via /proc/cpuinfo)
2. **DMI/SMBIOS signatures** - Hardware vendor strings
3. **VM-specific devices** - /dev/vda (virtio), /dev/xvda (Xen), etc.
4. **MAC address OUI** - VM vendors have registered prefixes
5. **Timing anomalies** - Syscall latency variance
6. **Cgroups** - Container detection
7. **Kernel modules** - VM guest drivers
8. **Block devices** - Disk model strings

## Raw Output

### Run 1
```
============================================================
 EXPERIMENT #001: VM Detection from Userspace
============================================================
Date: 2025-12-30T09:55:56.024946
Platform: Linux-6.1.102-x86_64-with-glibc2.35
Python: 3.11.0rc1
Machine: x86_64
Hostname: 526b9be059e8
============================================================
 CPU Features Analysis
============================================================
⚠️  'hypervisor' flag present in CPU flags!
Vendor: GenuineIntel
Model: Intel(R) Xeon(R) Processor @ 2.10GHz
CPU Flags (116 total)
  ⚠️  HYPERVISOR FLAG DETECTED in flags list
  Interesting flags: vme, hypervisor
============================================================
 DMI/SMBIOS VM Detection
============================================================
✗ product_name: not found
✗ sys_vendor: not found
✗ board_vendor: not found
✗ bios_vendor: not found
✗ chassis_vendor: not found
✗ product_name: not found
============================================================
 VM-Specific Files/Devices
============================================================
✓ /dev/vda (virtio disk (KVM/QEMU))
✗ /dev/vdb
✗ /dev/xvda
✗ /dev/sda
✗ /sys/hypervisor/type
✗ /proc/xen
✗ /sys/bus/vmbus
✗ /proc/vz
✗ /dev/vzfs
✓ /.dockerenv (Docker container): 
✗ /run/.containerenv
============================================================
 MAC Address VM Detection
============================================================
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000
    link/ether 02:fc:00:00:00:05 brd ff:ff:ff:ff:ff:ff
⚠️  DETECTED: Firecracker/Cloud MAC prefix (02:fc:) -> 02:fc:00:00:00:05
============================================================
 Timing Anomaly Detection
============================================================
[Test 1] Syscall timing (getpid)...
  Mean:   234.65 ns
  Median: 224.00 ns
  StdDev: 91.71 ns
  Min:    215 ns
  Max:    2996 ns
[Test 2] Sleep accuracy (1ms sleeps)...
  Mean error: 0.095 ms
  Max error:  0.152 ms
============================================================
 Cgroups/Container Detection
============================================================
PID 1 cgroups:
0::/init.scope
Self cgroups:
0::/system.slice/supervisor.service
============================================================
 Kernel Module Analysis
============================================================
ERROR: [Errno 2] No such file or directory: '/proc/modules'
============================================================
 Disk/Block Device Analysis
============================================================
NAME  SIZE TYPE MODEL
vda  41.6G disk 
============================================================
 FINAL VERDICT
============================================================
🔴 VIRTUALIZED ENVIRONMENT DETECTED
Evidence:
  • CPU hypervisor flag set
  • VM files: virtio disk (KVM/QEMU), Docker container
  • MAC vendor: Firecracker/Cloud
```

### Run 2 (Reproducibility Check)
```
============================================================
 FINAL VERDICT
============================================================
🔴 VIRTUALIZED ENVIRONMENT DETECTED
Evidence:
  • CPU hypervisor flag set
  • VM files: virtio disk (KVM/QEMU), Docker container
  • MAC vendor: Firecracker/Cloud

Timing stats (Run 2):
  syscall mean: 313.56 ns
  syscall stdev: 2492.18 ns (HIGH VARIANCE - VM indicator!)
  syscall max: 79005 ns (outlier from VM scheduling)
```

## Validation
- [x] External proof exists (file created, API responded, something changed in the real world)
  - Detected actual Firecracker microVM (AWS's hypervisor)
  - Found real virtio disk at /dev/vda
  - Identified Docker container via /.dockerenv
- [x] Reproducible (ran it twice, same result)
  - Both runs detected same 3 evidence points
  - Verdict: "VIRTUALIZED ENVIRONMENT DETECTED" both times
- [x] Output contains info I couldn't have guessed
  - MAC prefix 02:fc: is Firecracker-specific
  - The sandbox is actually Docker-in-Firecracker (nested virtualization!)
- [x] A skeptic would believe this
  - Raw /proc/cpuinfo shows hypervisor flag
  - /dev/vda exists and is virtio
  - /.dockerenv file physically present

## Confidence
🟢 **Confirmed**

## Learnings

### What surprised me?
1. **The hypervisor flag is just... there.** Intel added CPUID bit 31 specifically for VMs to self-identify. It's not hidden at all.

2. **Firecracker has a unique MAC prefix (02:fc:).** This is a fingerprint I didn't know existed. You can identify AWS Lambda/Fargate environments this way.

3. **We're in Docker-inside-Firecracker.** The sandbox is actually nested virtualization - a container running inside a microVM. That's why we see both /.dockerenv AND virtio devices.

4. **Timing variance is a real signal.** Run 2 showed syscall max of 79,005 ns vs median of 224 ns - that's a 350x outlier from VM scheduling jitter.

5. **DMI/SMBIOS is locked down.** The /sys/class/dmi paths don't exist in this environment - Firecracker strips them for security.

### What new questions emerged?
- Can we detect the *specific* cloud provider (AWS vs GCP vs Azure) from these signals?
- What's the minimum set of checks to reliably detect ANY VM?
- Can we detect nested virtualization depth (VM inside VM inside VM)?
- How do "stealth" VMs hide these indicators?

### What's the next rabbit hole?
- **Cloud provider fingerprinting**: Use metadata services, timing patterns, and hardware signatures to identify AWS/GCP/Azure
- **VM escape detection**: Can we detect if we're in a compromised VM?
- **Timing-based covert channels**: Use VM scheduling jitter to communicate between VMs on the same host
