from time import perf_counter, time
from datetime import datetime

def test(target, args=(), attempts=1000000):
    start = perf_counter()
    for _ in range(attempts):
        target(*args)
    elapsed = perf_counter() - start
    print(elapsed)


if __name__ == "__main__":
    def q1(string):
        return [num.strip() for num in string.replace('",', '').replace('"', '').split(',')]
    def q2(string):
        return [string[0:8].strip(), string[13:25].strip(), string[30:42].strip(), string[43:52].strip()]
    def q3(string):
        l = string.split(",")
        return [l[0].strip(), l[2].strip(), l[4].strip(), l[5].strip()]
    def f1(string):
        return [float(num) for num in string.replace('",', '').replace('"', '').split(',')]
    def f2(string):
        return [float(string[0:8]), float(string[13:25]), float(string[30:42]), float(string[43:52])]
    def dumb1(partial_data):
        converted_list = [""] * len(partial_data)
        for ii, label in enumerate(('Time [s]', 'Temperature A [K]', 'Temperature B [K]',
                                    'Capacitance [pF]', 'Loss Tangent', 'Voltage [V]', 'Frequency [Hz]')):
            if "time" in label.lower():
                converted_list[ii] = str(datetime.fromtimestamp(partial_data[ii]))
            elif "temperature" in label.lower():
                converted_list[ii] = f"{partial_data[ii]:s} K".rjust(20)
            elif "frequency" in label.lower():
                converted_list[ii] = f"{partial_data[ii]:s} Hz".rjust(20)
            elif "voltage" in label.lower():
                converted_list[ii] = f"{partial_data[ii]:s} V<sub>RMS</sub>".rjust(25)
            elif "capacitance" in label.lower():
                converted_list[ii] = f"{partial_data[ii]:s} pF".rjust(20)
            else:
                converted_list[ii] = f"{partial_data[ii]:s}".rjust(17)

    def dumb2(partial_data):
        converted_list = [str(datetime.fromtimestamp(partial_data[0])),
                          f"{partial_data[1]:s} K".rjust(20),
                          f"{partial_data[2]:s} K".rjust(20),
                          f"{partial_data[3]:s} pF".rjust(20),
                          f"{partial_data[4]:s}".rjust(17),
                          f"{partial_data[5]:s} V<sub>RMS</sub>".rjust(25),
                          f"{partial_data[6]:s} Hz".rjust(25)]
        ", ".join(converted_list)

    q = ' 14000.0," ", 0.9977124  ," ",-0.0000264  , 1.00    '
    li = ['14000.0', '0.9977124', '-0.0000264', '1.00']
    pd = [time(), '300.00', '297.01', '14000.0', '0.9977124', '-0.0000264', '1.00']
    test(dumb1, (pd,))
    test(dumb2, (pd,))
    # test(dumb3, (li,))
    # test(dumb2, (q,))
    # test(q1, (q,))
    # test(q2, (q,))
    # test(q3, (q,))
    # test(f1, (q,))
    # test(f2, (q,))
