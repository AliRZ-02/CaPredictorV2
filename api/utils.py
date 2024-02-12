def convert_time_to_float(time_str: str) -> float:
    data = time_str.split(":")
    mins, secs = data[0], data[1]

    return float(mins) + (float(secs) / 60)