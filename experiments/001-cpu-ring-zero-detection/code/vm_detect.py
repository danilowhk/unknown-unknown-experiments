#!/usr/bin/env python3
"""
Experiment #001: Can we detect we're in a VM from userspace?

Multiple detection vectors:
1. CPUID hypervisor bit (via /proc/cpuinfo)
2. DMI/SMBIOS signatures
3. VM-specific devices and files
4. MAC address OUI fingerprinting
5. Timing anomalies via Python's perf_counter
6. Memory/disk fingerprinting
"""

import time
import subprocess
import os
import platform
import statistics
import json
from datetime import datetime

def banner(text):
    print(f"\n{'='*60}")
    print(f" {text}")
    print('='*60)

def check_cpu_features():
    """Check /proc/cpuinfo for VM hints"""
    banner("CPU Features Analysis")
    
    results = {
        'hypervisor_flag': False,
        'vendor': None,
        'model': None,
        'flags': []
    }
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        # Look for hypervisor flag
        if 'hypervisor' in cpuinfo:
            print("⚠️  'hypervisor' flag present in CPU flags!")
            results['hypervisor_flag'] = True
        
        # Print relevant lines (only first CPU)
        seen_model = False
        for line in cpuinfo.split('\n'):
            if 'model name' in line.lower() and not seen_model:
                results['model'] = line.split(':')[1].strip()
                print(f"Model: {results['model']}")
                seen_model = True
            elif 'vendor_id' in line.lower() and not results['vendor']:
                results['vendor'] = line.split(':')[1].strip()
                print(f"Vendor: {results['vendor']}")
            elif 'flags' in line.lower() and not results['flags']:
                flags = line.split(':')[1].strip().split()
                results['flags'] = flags
                print(f"CPU Flags ({len(flags)} total)")
                if 'hypervisor' in flags:
                    print("  ⚠️  HYPERVISOR FLAG DETECTED in flags list")
                # Show some interesting flags
                interesting = ['vmx', 'svm', 'hypervisor', 'kvm', 'vme']
                found = [f for f in flags if f in interesting]
                if found:
                    print(f"  Interesting flags: {', '.join(found)}")
    except Exception as e:
        print(f"ERROR reading cpuinfo: {e}")
    
    return results

def check_dmi_info():
    """Check DMI/SMBIOS for VM signatures"""
    banner("DMI/SMBIOS VM Detection")
    
    dmi_checks = [
        '/sys/class/dmi/id/product_name',
        '/sys/class/dmi/id/sys_vendor',
        '/sys/class/dmi/id/board_vendor',
        '/sys/class/dmi/id/bios_vendor',
        '/sys/class/dmi/id/chassis_vendor',
        '/sys/devices/virtual/dmi/id/product_name',
    ]
    
    vm_signatures = ['vmware', 'virtualbox', 'kvm', 'qemu', 'xen', 'hyper-v', 'parallels', 'bochs', 'amazon', 'google', 'microsoft']
    
    results = {}
    detected_vm = None
    
    for path in dmi_checks:
        try:
            with open(path, 'r') as f:
                value = f.read().strip()
                results[path] = value
                print(f"✓ {os.path.basename(path)}: {value}")
                
                # Check for VM signatures
                for sig in vm_signatures:
                    if sig in value.lower():
                        detected_vm = sig
                        print(f"  ⚠️  VM SIGNATURE DETECTED: {sig}")
        except FileNotFoundError:
            results[path] = None
            print(f"✗ {os.path.basename(path)}: not found")
        except PermissionError:
            results[path] = "PERMISSION_DENIED"
            print(f"✗ {os.path.basename(path)}: permission denied")
        except Exception as e:
            results[path] = f"ERROR: {e}"
            print(f"✗ {os.path.basename(path)}: {e}")
    
    results['detected_vm'] = detected_vm
    return results

def check_vm_files():
    """Check for VM-specific files and devices"""
    banner("VM-Specific Files/Devices")
    
    vm_indicators = {
        '/dev/vda': 'virtio disk (KVM/QEMU)',
        '/dev/vdb': 'virtio disk (KVM/QEMU)',
        '/dev/xvda': 'Xen disk',
        '/dev/sda': 'standard disk',
        '/sys/hypervisor/type': 'Xen hypervisor',
        '/proc/xen': 'Xen',
        '/sys/bus/vmbus': 'Hyper-V',
        '/proc/vz': 'OpenVZ',
        '/dev/vzfs': 'OpenVZ',
        '/.dockerenv': 'Docker container',
        '/run/.containerenv': 'Podman container',
    }
    
    results = {}
    detected = []
    
    for path, desc in vm_indicators.items():
        exists = os.path.exists(path)
        results[path] = exists
        if exists:
            detected.append(desc)
            try:
                if os.path.isfile(path):
                    with open(path, 'r') as f:
                        content = f.read().strip()[:100]
                    print(f"✓ {path} ({desc}): {content}")
                else:
                    print(f"✓ {path} ({desc})")
            except:
                print(f"✓ {path} ({desc}) - unreadable")
        else:
            print(f"✗ {path}")
    
    results['detected'] = detected
    return results

def check_mac_address():
    """Check MAC address OUI for VM vendors"""
    banner("MAC Address VM Detection")
    
    vm_ouis = {
        '00:50:56': 'VMware',
        '00:0c:29': 'VMware',
        '00:1c:42': 'Parallels',
        '00:03:ff': 'Microsoft Hyper-V',
        '00:15:5d': 'Microsoft Hyper-V',
        '00:16:3e': 'Xen',
        '08:00:27': 'VirtualBox',
        '52:54:00': 'QEMU/KVM',
        'fa:16:3e': 'OpenStack',
        '02:42:': 'Docker',
        '02:fc:': 'Firecracker/Cloud',
    }
    
    results = {'macs': [], 'detected': []}
    
    try:
        result = subprocess.run(['ip', 'link'], capture_output=True, text=True)
        output = result.stdout
        print(output)
        
        # Extract MAC addresses
        import re
        macs = re.findall(r'link/ether ([0-9a-f:]+)', output, re.IGNORECASE)
        results['macs'] = macs
        
        for mac in macs:
            mac_prefix = mac[:8].lower()
            for oui, vendor in vm_ouis.items():
                if mac.lower().startswith(oui.lower()):
                    results['detected'].append({'mac': mac, 'vendor': vendor})
                    print(f"⚠️  DETECTED: {vendor} MAC prefix ({oui}) -> {mac}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    return results

def timing_test():
    """Test for timing anomalies that might indicate VM"""
    banner("Timing Anomaly Detection")
    
    results = {
        'syscall_times': [],
        'sleep_accuracy': [],
        'stats': {}
    }
    
    # Test 1: Measure time to make simple syscalls
    print("\n[Test 1] Syscall timing (getpid)...")
    times = []
    for _ in range(1000):
        start = time.perf_counter_ns()
        os.getpid()
        end = time.perf_counter_ns()
        times.append(end - start)
    
    results['syscall_times'] = times
    mean = statistics.mean(times)
    median = statistics.median(times)
    stdev = statistics.stdev(times)
    results['stats']['syscall'] = {
        'mean_ns': mean,
        'median_ns': median,
        'stdev_ns': stdev,
        'min_ns': min(times),
        'max_ns': max(times)
    }
    
    print(f"  Mean:   {mean:.2f} ns")
    print(f"  Median: {median:.2f} ns")
    print(f"  StdDev: {stdev:.2f} ns")
    print(f"  Min:    {min(times)} ns")
    print(f"  Max:    {max(times)} ns")
    
    # High variance often indicates VM
    if stdev > mean * 0.5:
        print(f"  ⚠️  High variance detected - possible VM indicator")
    
    # Test 2: Sleep accuracy
    print("\n[Test 2] Sleep accuracy (1ms sleeps)...")
    sleep_errors = []
    for _ in range(100):
        target = 0.001  # 1ms
        start = time.perf_counter()
        time.sleep(target)
        actual = time.perf_counter() - start
        error = (actual - target) * 1000  # in ms
        sleep_errors.append(error)
    
    results['sleep_accuracy'] = sleep_errors
    mean_err = statistics.mean(sleep_errors)
    results['stats']['sleep'] = {
        'mean_error_ms': mean_err,
        'max_error_ms': max(sleep_errors)
    }
    
    print(f"  Mean error: {mean_err:.3f} ms")
    print(f"  Max error:  {max(sleep_errors):.3f} ms")
    
    if mean_err > 1.0:
        print(f"  ⚠️  High sleep error - possible VM/container indicator")
    
    return results

def check_cgroups():
    """Check cgroups for container indicators"""
    banner("Cgroups/Container Detection")
    
    results = {'in_container': False, 'cgroup_info': None}
    
    try:
        with open('/proc/1/cgroup', 'r') as f:
            cgroup = f.read()
            results['cgroup_info'] = cgroup
            print(f"PID 1 cgroups:\n{cgroup}")
            
            if 'docker' in cgroup.lower():
                results['in_container'] = True
                print("⚠️  Docker container detected!")
            if 'kubepods' in cgroup.lower():
                results['in_container'] = True
                print("⚠️  Kubernetes pod detected!")
            if 'lxc' in cgroup.lower():
                results['in_container'] = True
                print("⚠️  LXC container detected!")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Also check /proc/self/cgroup
    try:
        with open('/proc/self/cgroup', 'r') as f:
            self_cgroup = f.read()
            print(f"\nSelf cgroups:\n{self_cgroup}")
    except:
        pass
    
    return results

def check_kernel_modules():
    """Check loaded kernel modules for VM indicators"""
    banner("Kernel Module Analysis")
    
    vm_modules = {
        'kvm': 'KVM host',
        'kvm_intel': 'KVM host (Intel)',
        'kvm_amd': 'KVM host (AMD)',
        'vboxdrv': 'VirtualBox host',
        'vboxguest': 'VirtualBox guest',
        'vmw_balloon': 'VMware guest',
        'vmw_vmci': 'VMware guest',
        'vmwgfx': 'VMware guest',
        'hv_vmbus': 'Hyper-V guest',
        'hv_storvsc': 'Hyper-V guest',
        'xen_blkfront': 'Xen guest',
        'virtio': 'virtio (KVM/QEMU)',
        'virtio_pci': 'virtio (KVM/QEMU)',
        'virtio_blk': 'virtio (KVM/QEMU)',
        'virtio_net': 'virtio (KVM/QEMU)',
    }
    
    results = {'modules': [], 'detected': []}
    
    try:
        with open('/proc/modules', 'r') as f:
            modules = f.read()
        
        loaded = [line.split()[0] for line in modules.strip().split('\n') if line]
        results['modules'] = loaded
        
        print(f"Loaded modules ({len(loaded)} total):")
        
        for mod, desc in vm_modules.items():
            if mod in loaded:
                results['detected'].append({'module': mod, 'type': desc})
                print(f"  ⚠️  {mod} ({desc})")
        
        # Show all loaded modules
        print(f"\nAll modules: {', '.join(loaded[:20])}{'...' if len(loaded) > 20 else ''}")
        
    except Exception as e:
        print(f"ERROR: {e}")
    
    return results

def check_disk_info():
    """Check disk information for VM indicators"""
    banner("Disk/Block Device Analysis")
    
    results = {'devices': [], 'detected': []}
    
    try:
        result = subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,MODEL'], capture_output=True, text=True)
        print(result.stdout)
        
        vm_disk_names = ['VBOX', 'QEMU', 'Virtual', 'VMware', 'Xen']
        for name in vm_disk_names:
            if name.lower() in result.stdout.lower():
                results['detected'].append(name)
                print(f"⚠️  VM disk signature: {name}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    return results

def generate_verdict(all_results):
    """Generate final verdict based on all evidence"""
    banner("FINAL VERDICT")
    
    evidence = []
    
    if all_results.get('cpu', {}).get('hypervisor_flag'):
        evidence.append("CPU hypervisor flag set")
    
    if all_results.get('dmi', {}).get('detected_vm'):
        evidence.append(f"DMI signature: {all_results['dmi']['detected_vm']}")
    
    if all_results.get('files', {}).get('detected'):
        evidence.append(f"VM files: {', '.join(all_results['files']['detected'])}")
    
    if all_results.get('mac', {}).get('detected'):
        for d in all_results['mac']['detected']:
            evidence.append(f"MAC vendor: {d['vendor']}")
    
    if all_results.get('cgroups', {}).get('in_container'):
        evidence.append("Container cgroup detected")
    
    if all_results.get('modules', {}).get('detected'):
        for d in all_results['modules']['detected']:
            evidence.append(f"Kernel module: {d['module']} ({d['type']})")
    
    if evidence:
        print("🔴 VIRTUALIZED ENVIRONMENT DETECTED")
        print("\nEvidence:")
        for e in evidence:
            print(f"  • {e}")
    else:
        print("🟢 No clear VM indicators found (could be bare metal or well-hidden VM)")
    
    return {
        'is_vm': len(evidence) > 0,
        'confidence': 'high' if len(evidence) >= 3 else 'medium' if len(evidence) >= 1 else 'low',
        'evidence': evidence
    }

def main():
    print("=" * 60)
    print(" EXPERIMENT #001: VM Detection from Userspace")
    print("=" * 60)
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Platform: {platform.platform()}")
    print(f"Python: {platform.python_version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Hostname: {platform.node()}")
    
    all_results = {}
    
    # Run all detection methods
    all_results['cpu'] = check_cpu_features()
    all_results['dmi'] = check_dmi_info()
    all_results['files'] = check_vm_files()
    all_results['mac'] = check_mac_address()
    all_results['timing'] = timing_test()
    all_results['cgroups'] = check_cgroups()
    all_results['modules'] = check_kernel_modules()
    all_results['disk'] = check_disk_info()
    
    # Generate verdict
    verdict = generate_verdict(all_results)
    all_results['verdict'] = verdict
    
    # Save raw JSON results
    print("\n" + "=" * 60)
    print(" RAW JSON OUTPUT")
    print("=" * 60)
    
    # Convert to JSON-safe format
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    json_output = json.dumps(make_serializable(all_results), indent=2)
    print(json_output)
    
    return all_results

if __name__ == '__main__':
    main()
