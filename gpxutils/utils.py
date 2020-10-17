def sd_to_dm(lat, lon):
    """Signed decimal coordinates to geographical degrees coordinates.

    Converts a signed decimal co-ordinate to a geographical
    co-ordinate given in "degrees/minutes" dddmm.mmmm format
    (eg, "12319.943281" = 123 degrees, 19.943281 minutes)

    """
    # (48.0680059, -1.7304015) → (("4804.080354", "N"), ("143.82409", "W")
    lat_sign = "S" if lat < 0 else "N"
    abs_lat = abs(lat)
    lat_hours = int(abs_lat)
    lat_minutes = (abs_lat - lat_hours) * 60

    lon_sign = "W" if lon < 0 else "E"
    abs_lon = abs(lon)
    lon_hours = int(abs_lon)
    lon_minutes = (abs_lon - lon_hours) * 60

    lat_minutes_text = f"{lat_minutes:.4f}".zfill(7)
    lon_minutes_text = f"{lon_minutes:.4f}".zfill(7)

    return (
        (f"{lat_hours}{lat_minutes_text}".zfill(9), lat_sign),
        (f"{lon_hours}{lon_minutes_text}".zfill(10), lon_sign),
    )
