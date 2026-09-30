from __future__ import annotations

COMMANDS = {
    "cisco_ios": {
        "running_config": "show running-config",
        "facts": "show version",
        "interfaces": "show interfaces status",
        "bgp": "show ip bgp summary",
        "ospf": "show ip ospf neighbor",
        "lldp": "show lldp neighbors detail",
        "mac": "show mac address-table",
        "arp": "show ip arp",
        "ntp": "show ntp associations",
        "snmp": "show running-config | include snmp-server",
        "aaa": "show running-config | section aaa",
        "logging": "show logging",
        "stp": "show spanning-tree summary",
        "errors": "show interfaces counters errors",
        "routes": "show ip route",
        "acl": "show access-lists",
        "vlan": "show vlan brief",
    },
    "cisco_xe": {},
    "cisco_nxos": {
        "running_config": "show running-config",
        "facts": "show version",
        "interfaces": "show interface status",
        "bgp": "show bgp ipv4 unicast summary",
        "ospf": "show ip ospf neighbors",
        "lldp": "show lldp neighbors detail",
        "mac": "show mac address-table",
        "arp": "show ip arp",
        "ntp": "show ntp peers",
        "snmp": "show running-config | include snmp-server",
        "aaa": "show running-config aaa",
        "logging": "show logging last 100",
        "stp": "show spanning-tree summary",
        "errors": "show interface counters errors",
        "routes": "show ip route",
        "acl": "show access-lists",
        "vlan": "show vlan brief",
    },
    "arista_eos": {
        "running_config": "show running-config",
        "facts": "show version",
        "interfaces": "show interfaces status",
        "bgp": "show ip bgp summary",
        "ospf": "show ip ospf neighbor",
        "lldp": "show lldp neighbors detail",
        "mac": "show mac address-table",
        "arp": "show arp",
        "ntp": "show ntp associations",
        "snmp": "show running-config | section snmp-server",
        "aaa": "show running-config | section aaa",
        "logging": "show logging last 100",
        "stp": "show spanning-tree summary",
        "errors": "show interfaces counters errors",
        "routes": "show ip route",
        "acl": "show access-lists",
        "vlan": "show vlan",
    },
    "juniper_junos": {
        "running_config": "show configuration | display set",
        "facts": "show version",
        "interfaces": "show interfaces terse",
        "bgp": "show bgp summary",
        "ospf": "show ospf neighbor",
        "lldp": "show lldp neighbors detail",
        "mac": "show ethernet-switching table",
        "arp": "show arp no-resolve",
        "ntp": "show ntp associations",
        "snmp": "show configuration snmp | display set",
        "aaa": "show configuration system authentication-order | display set",
        "logging": "show log messages | last 100",
        "stp": "show spanning-tree bridge",
        "errors": "show interfaces extensive | match error",
        "routes": "show route",
        "acl": "show configuration firewall | display set",
        "vlan": "show vlans",
    },
}
COMMANDS["cisco_xe"] = COMMANDS["cisco_ios"].copy()


def platform_key(device: dict) -> str:
    return device.get("platform") or device.get("device_type", "cisco_ios")


def get_command(device: dict, key: str) -> str:
    override = device.get("commands", {}).get(key)
    if override:
        return override
    platform = platform_key(device)
    if platform not in COMMANDS or key not in COMMANDS[platform]:
        raise KeyError(f"No command mapping for platform={platform!r}, key={key!r}. Add an override in inventory.yml.")
    return COMMANDS[platform][key]

# Additional audit commands used by Pro modules.
_EXTRA = {
    "cisco_ios": {
        "mtu": "show interfaces | include ^[A-Za-z].*line protocol|MTU",
        "uptime": "show version | include uptime",
    },
    "cisco_xe": {
        "mtu": "show interfaces | include ^[A-Za-z].*line protocol|MTU",
        "uptime": "show version | include uptime",
    },
    "cisco_nxos": {
        "mtu": "show interface | include ^[A-Za-z].*is (up|down)|MTU",
        "uptime": "show version | include uptime",
    },
    "arista_eos": {
        "mtu": "show interfaces | include ^[A-Za-z].*line protocol|MTU",
        "uptime": "show version | include uptime",
    },
    "juniper_junos": {
        "mtu": "show interfaces detail | match \"Physical interface|MTU\"",
        "uptime": "show system uptime",
    },
}
for _platform, _values in _EXTRA.items():
    COMMANDS.setdefault(_platform, {}).update(_values)
