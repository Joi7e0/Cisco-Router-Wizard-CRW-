# backend/protocols.py
# Генерація конфігурації протоколів маршрутизації
def _mask_to_wildcard(mask: str) -> str:

    try:
        if not isinstance(mask, str):
            raise TypeError(f"Mask must be str, got {type(mask)}")
        parts = mask.split('.')
        if len(parts) != 4:
            raise ValueError("Mask must have exactly 4 octets")

        wildcard_parts = []
        for p in parts:
            try:
                octet = int(p)
            except ValueError:
                raise ValueError(f"Invalid octet value: {p}")
            if not (0 <= octet <= 255):
                raise ValueError(f"Octet out of range: {octet}")
            wildcard_parts.append(str(255 - octet))

        return '.'.join(wildcard_parts)
    except (ValueError, TypeError) as e:
        # Log to stdout for test visibility; in production consider using logging
        print(f"Error in _mask_to_wildcard: {e}")
        return "0.0.0.0"

# Генерація конфігурації протоколу маршрутизації
def generate_protocol_config(protocol: str, router_id: str, networks: list[tuple[str, str]]) -> list[str]:
    try:
        if not isinstance(protocol, str) or not isinstance(router_id, str):
            raise TypeError("Protocol and router_id must be strings")

        proto = protocol.upper().strip()
        cfg = []

        if proto == "OSPF":
            cfg.append("!")
            cfg.append("router ospf 1")
            cfg.append(f" router-id {router_id}")
            for item in networks:
                try:
                    net_ip, net_mask = item
                    wildcard = _mask_to_wildcard(net_mask)
                    cfg.append(f" network {net_ip} {wildcard} area 0")
                except Exception as e:
                    cfg.append(f"! Error in network config: {e}")
            cfg.append(" exit")
        elif proto == "RIP":
            cfg.append("!")
            cfg.append("router rip")
            cfg.append(" version 2")
            for item in networks:
                try:
                    net_ip, _ = item
                    cfg.append(f" network {net_ip}")
                except Exception as e:
                    cfg.append(f"! Error in network config: {e}")
            cfg.append(" no auto-summary")
            cfg.append(" exit")
        elif proto == "EIGRP":
            cfg.append("!")
            cfg.append("router eigrp 100")
            for item in networks:
                try:
                    net_ip, _ = item
                    cfg.append(f" network {net_ip}")
                except Exception as e:
                    cfg.append(f"! Error in network config: {e}")
            cfg.append(" no auto-summary")
            cfg.append(" exit")
        elif proto == "BGP":
            cfg.append("!")
            cfg.append("router bgp 65000")
            cfg.append(" bgp log-neighbor-changes")
            cfg.append(" neighbor 1.1.1.2 remote-as 65001")
            cfg.append(" exit")
        elif proto == "IS-IS":
            cfg.append("!")
            cfg.append("router isis")
            cfg.append(" net 49.0001.0000.0000.0001.00")
            cfg.append(" is-type level-2-only")
            cfg.append(" exit")
        else:
            cfg.append("! No routing protocol selected")

        return cfg
    except (TypeError, ValueError) as e:
        print(f"Error in generate_protocol_config: {e}")
        return ["! Routing protocol error: Invalid input"]