import threading
import time
from datetime import datetime
import numpy as np

timestamp_format_list = {
    "type1": "%Y-%m-%d %H:%M:%S.%f",
    "type2": "%Y/%m/%d %H:%M:%S.%f",
    "type3": "%H:%M:%S.%f",
}


def create_line(pct: float, timestamp_format: str, msg: str | None = None):
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime(timestamp_format)[:-3]

    progress = pct * 100
    if msg is not None:
        entry = f"[{timestamp_str}] {progress:.2f}% {msg}"
    else:
        entry = f"[{timestamp_str}] {progress:.2f}%"
    return entry


def write_log_file(
    file_path: str,
    format_type: str,
    cnt: int,
    dt_mean: float,
    dt_var: float,
):

    with open(file_path, "w") as file:
        file.write("<<<BEGIN>>>\n")
        file.flush()

        for i in range(cnt):
            pct = (i + 1) / cnt

            try_flag = np.random.random()
            if try_flag < 0.03:
                entry = create_line(
                    pct,
                    timestamp_format_list[format_type],
                    msg=" an error occurred.",
                )
            elif try_flag < 0.06:
                entry = create_line(
                    pct,
                    timestamp_format_list[format_type],
                    msg=" a warning occurred.",
                )
            elif try_flag < 0.10:
                entry = " an error occurred."
            elif try_flag < 0.13:
                entry = " an NaN occurred."
            elif try_flag < 0.15:
                entry = " a warning occurred."
            else:
                entry = create_line(pct, timestamp_format_list[format_type])

            file.write(entry + "\n")
            file.flush()

            dt = max([np.random.normal(dt_mean, dt_var), 0.01])
            time.sleep(dt)

        file.write("<<<END>>>")
        file.flush()


def loop_task(
    file_path: str,
    format_type: str,
    cnt: int,
    dt_mean: float,
    dt_var: float,
):

    thread_id = threading.get_ident()

    loop = 0
    while True:
        print(f"[{thread_id}] Starting loop {loop + 1}")
        write_log_file(
            file_path,
            format_type,
            cnt,
            dt_mean,
            dt_var,
        )
        print(f"[{thread_id}] Completed loop {loop + 1}")
        loop += 1


def main():
    thread1 = threading.Thread(
        target=loop_task,
        args=(
            "./progress1.log",  # 60s
            "type1",
            120,
            0.5,
            0.02,
        ),
    )
    thread2 = threading.Thread(
        target=loop_task,
        args=(
            "./progress2.log",  # 60s
            "type2",
            60,
            1.0,
            0.03,
        ),
    )

    thread3 = threading.Thread(
        target=loop_task,
        args=(
            "./progress3.log",  # 60s
            "type3",
            300,
            0.2,
            0,
        ),
    )

    thread1.start()
    thread2.start()
    thread3.start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
