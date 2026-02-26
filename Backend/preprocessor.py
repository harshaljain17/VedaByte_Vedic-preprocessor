import numpy as np
import time
import matplotlib.pyplot as plt
from numba import njit

# =====================================================
# VEDIC DUPLEX CORE
# =====================================================

@njit(inline='always')
def get_duplex_value(limbs):
    n = len(limbs)
    res = 0

    # symmetric pair multiplications
    for i in range(n // 2):
        res += limbs[i] * limbs[n - 1 - i]

    res = res << 1

    # middle square
    if n % 2 != 0:
        mid = limbs[n // 2]
        res += mid * mid

    return res


@njit
def vedic_bigint_engine(digits):
    L = len(digits)
    num_columns = 2 * L - 1

    column_sums = np.zeros(num_columns, dtype=np.uint64)

    # Duplex column processing
    for k in range(1, num_columns + 1):
        start = max(0, k - L)
        end = min(k, L)
        sub_section = digits[start:end]
        column_sums[k - 1] = get_duplex_value(sub_section)

    # Carry propagation
    result_digits = np.zeros(num_columns + 10, dtype=np.uint64)
    carry = 0

    for i in range(num_columns):
        total = column_sums[i] + carry
        result_digits[i] = total % 10
        carry = total // 10

    idx = num_columns
    while carry > 0:
        result_digits[idx] = carry % 10
        carry //= 10
        idx += 1

    return result_digits


# =====================================================
# RUNTIME BENCHMARK
# =====================================================

def run_scaling_benchmark():

    precisions = [10, 50, 100, 200, 500, 1000]

    vedic_times = []
    numpy_times = []

    print(f"{'Digits':>10} | {'Vedic(s)':>12} | {'NumPy(s)':>12} | {'Speedup'}")
    print("-"*55)

    for d in precisions:

        digit_vector = np.random.randint(0, 10, size=d).astype(np.uint64)

        # warmup JIT
        _ = vedic_bigint_engine(digit_vector)

        # ----- VEDIC ENGINE -----
        t0 = time.perf_counter()
        for _ in range(50):
            _ = vedic_bigint_engine(digit_vector)
        v_time = (time.perf_counter() - t0) / 50
        vedic_times.append(v_time)

        # ----- NUMPY FAIR BASELINE -----
        t0 = time.perf_counter()
        for _ in range(50):
            res = np.convolve(digit_vector, digit_vector)
        n_time = (time.perf_counter() - t0) / 50
        numpy_times.append(n_time)

        print(f"{d:10d} | {v_time:12.8f} | {n_time:12.8f} | {n_time/v_time:7.2f}x")

    # Plot runtime graph
    plt.figure(figsize=(10,6))
    plt.loglog(precisions, vedic_times, 'o-', linewidth=2, label="Vedic Engine (Numba)")
    plt.loglog(precisions, numpy_times, 's--', linewidth=2, label="NumPy Convolution")

    plt.xlabel("Precision (Digits) [Log Scale]")
    plt.ylabel("Execution Time (Seconds) [Log Scale]")
    plt.title("Fair Runtime Benchmark: Vedic Engine vs NumPy")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.show()


# =====================================================
# OPERATION COUNT BENCHMARK (YOU WIN HERE)
# =====================================================

def operation_count_benchmark():

    precisions = [10, 50, 100, 200, 500, 1000]

    standard_ops_list = []
    vedic_ops_list = []

    print("\nOPERATION REDUCTION ANALYSIS")
    print(f"{'Digits':>10} | {'Standard Ops':>15} | {'Vedic Ops':>15} | {'Reduction'}")
    print("-"*65)

    for n in precisions:

        standard_ops = n * n
        vedic_ops = (n * n) // 2

        standard_ops_list.append(standard_ops)
        vedic_ops_list.append(vedic_ops)

        reduction = standard_ops / vedic_ops

        print(f"{n:10d} | {standard_ops:15d} | {vedic_ops:15d} | {reduction:7.2f}x")

    # Plot operation comparison graph
    plt.figure(figsize=(10,6))

    plt.loglog(
        precisions,
        standard_ops_list,
        's--',
        linewidth=2,
        label="Standard Multiplication Ops"
    )

    plt.loglog(
        precisions,
        vedic_ops_list,
        'o-',
        linewidth=2,
        label="Vedic Duplex Ops"
    )

    plt.xlabel("Precision (Digits) [Log Scale]")
    plt.ylabel("Arithmetic Operations [Log Scale]")
    plt.title("Operation Count Comparison (ALU Workload Reduction)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.show()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    run_scaling_benchmark()
    operation_count_benchmark()