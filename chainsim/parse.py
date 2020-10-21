def parse_data():
    # Parse the data
    lowest_times = {}
    with open("data/detection_time.txt") as detect_time_file:
        for line in detect_time_file.readlines():
            parts = line.strip().split(",")
            public_key = parts[0]
            detect_time = int(parts[1])

            if public_key not in lowest_times:
                lowest_times[public_key] = 1000000000000000

            if detect_time < lowest_times[public_key]:
                lowest_times[public_key] = detect_time

    with open("data/fraud_time.txt") as fraud_time_file:
        for line in fraud_time_file.readlines():
            parts = line.strip().split(",")
            public_key = parts[0]
            fraud_time = int(parts[1])

            if public_key in lowest_times:
                lowest_times[public_key] -= fraud_time
            else:
                print("The fraud of peer %s is not detected!" % public_key)

    with open("data/detect_times.txt", "w") as out_file:
        for public_key, detect_time in lowest_times.items():
            out_file.write("%s,%d\n" % (public_key, detect_time))

    # Compute the average lowest detection time
    avg_time = 0
    for detect_time in lowest_times.values():
        avg_time += detect_time
    avg_time /= len(list(lowest_times.values()))

    with open("data/avg_detect_time.txt", "w") as detect_time_file:
        detect_time_file.write("%d" % avg_time)

    print("Parsing data done!")
