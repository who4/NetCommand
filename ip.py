import socket
import requests

OPENCAGE_API_KEY = "64a4662212c044e2b53fded49b857d01"


def get_public_ip():
    r = requests.get("https://api.ipify.org?format=json", timeout=10)
    return r.json()["ip"]


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def get_ip_data(ip):
    url = (
        f"http://ip-api.com/json/{ip}"
        "?fields=status,message,country,regionName,city,lat,lon,timezone,"
        "isp,org,as,query,proxy,hosting"
    )
    r = requests.get(url, timeout=10)
    data = r.json()

    if data.get("status") != "success":
        raise Exception(data.get("message", "IP lookup failed"))

    return data


def reverse_geocode(lat, lon):
    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": f"{lat},{lon}",
        "key": OPENCAGE_API_KEY,
        "language": "en",
        "no_annotations": 0,
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    return data["results"][0] if data["results"] else None


def section(title):
    print(f"\n=== {title} ===")


def vpn_verdict(proxy, hosting):
    if hosting:
        return "HOSTING / DATACENTER"
    if proxy:
        return "VPN / PROXY"
    return "NORMAL / RESIDENTIAL"


def main():
    public_ip = get_public_ip()
    local_ip = get_local_ip()

    ip_data = get_ip_data(public_ip)
    geo = reverse_geocode(ip_data["lat"], ip_data["lon"])

    section("NETWORK")
    print(f"Public IP : {public_ip}")
    print(f"Local IP  : {local_ip}")

    section("LOCATION (IP GEO)")
    print(f"Country  : {ip_data['country']}")
    print(f"Region   : {ip_data['regionName']}")
    print(f"City     : {ip_data['city']}")
    print(f"Timezone : {ip_data['timezone']}")
    print(f"Lat/Lon  : {ip_data['lat']}, {ip_data['lon']}")

    section("PROVIDER")
    print(f"ISP      : {ip_data['isp']}")
    print(f"Org      : {ip_data['org']}")
    print(f"ASN      : {ip_data['as']}")

    section("ANONYMITY CHECK")
    print(f"Proxy/VPN Detected : {ip_data['proxy']}")
    print(f"Hosting Provider   : {ip_data['hosting']}")
    print(f"Verdict            : {vpn_verdict(ip_data['proxy'], ip_data['hosting'])}")

    if geo:
        comp = geo.get("components", {})
        ann = geo.get("annotations", {})

        section("DETAILED ADDRESS (OpenCage)")
        print(f"Address      : {geo.get('formatted', 'N/A')}")
        print(f"Continent    : {comp.get('continent', 'N/A')}")
        print(f"Postal Code  : {comp.get('postcode', 'N/A')}")
        print(f"Currency     : {ann.get('currency', {}).get('name', 'N/A')}")
        print(f"Calling Code : +{ann.get('callingcode', 'N/A')}")

    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
    finally:
        input("\nPress Enter to exit...")

