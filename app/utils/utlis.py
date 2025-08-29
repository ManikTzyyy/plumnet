# utils.py

def format_rupiah(value):
    try:
        value = int(value)
        return "Rp {:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value

def parse_mikrotik_output(output: str):
    result = {}
    parts = output.split(" ")
    key = None
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            result[k.strip()] = v.strip()
            key = k.strip()
        else:
            if key:  # kalau value mengandung spasi, gabungkan
                result[key] += " " + part.strip()
    return result
