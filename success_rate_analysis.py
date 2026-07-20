"""Sweep every valid base a for N=15 and N=21 and measure how often Shor's
algorithm actually succeeds per base.

This deliberately calls run_shor_algorithm(N, a) directly (the fixed-base
period-finding routine), NOT factor_number (which auto-retries with random
bases). The goal is to see per-base behavior, including the mathematically
expected failure modes discussed in discussion.md and the project's past
audit: an odd multiplicative order of a mod N, or a^(r/2) = -1 mod N. Both
make period-finding uninformative for that base and are not bugs.

Each outcome is classified as one of:
  - success:            returned a correct nontrivial factorization of N
  - expected_failure:   failed, and the true (classically computed) order
                         of a mod N explains why (odd order, or a^(r/2) = -1)
  - unexpected_failure: failed for no known mathematical reason - flagged,
                         not hidden, since this would indicate a real bug

Produces examples/success_rate_by_base.png.
"""
import time
from math import gcd

import matplotlib.pyplot as plt

from shor_algorithm import run_shor_algorithm


def multiplicative_order(a, N):
    """Classically compute the true multiplicative order of a mod N.

    N is tiny in this project (15, 21), so a direct loop is fine - no need
    for anything cleverer than repeated multiplication.
    """
    x = a % N
    r = 1
    while x != 1:
        x = (x * a) % N
        r += 1
        if r > N:
            return None  # shouldn't happen when gcd(a, N) == 1
    return r


def valid_bases(N):
    """Every integer 2 <= a < N with gcd(a, N) == 1."""
    return [a for a in range(2, N) if gcd(a, N) == 1]


def classify(N, a, f1, f2, r_true):
    """Decide success / expected_failure / unexpected_failure for one base."""
    success = (
        f1 is not None and f2 is not None
        and f1 * f2 == N and 1 < f1 < N and 1 < f2 < N
    )
    if success:
        return "success", f"factors=({f1},{f2}) r_true={r_true}"

    odd_order = (r_true is not None) and (r_true % 2 == 1)
    neg_one = False
    if r_true is not None and r_true % 2 == 0:
        neg_one = pow(a, r_true // 2, N) == N - 1

    if odd_order or neg_one:
        reason = "odd order" if odd_order else "a^(r/2) = -1 mod N"
        return "expected_failure", f"r_true={r_true} reason={reason}"

    return "unexpected_failure", f"r_true={r_true} (no expected reason found)"


def sweep(N):
    """Run run_shor_algorithm(N, a) for every valid base a and classify it."""
    results = []
    for a in valid_bases(N):
        r_true = multiplicative_order(a, N)
        t0 = time.time()
        f1, f2 = run_shor_algorithm(N, a)
        elapsed = time.time() - t0
        outcome, detail = classify(N, a, f1, f2, r_true)
        print(f"N={N} a={a:>2}: {outcome:<18} {detail} ({elapsed:.1f}s)", flush=True)
        results.append((a, outcome, detail))
    return results


def plot_results(results_by_N, out_path="examples/success_rate_by_base.png"):
    colors = {
        "success": "tab:green",
        "expected_failure": "tab:orange",
        "unexpected_failure": "tab:red",
    }
    labels = {
        "success": "Success",
        "expected_failure": "Expected failure (odd order, or a^(r/2) = -1 mod N)",
        "unexpected_failure": "Unexpected failure (possible bug)",
    }

    fig, axes = plt.subplots(
        1, len(results_by_N), figsize=(7 * len(results_by_N), 6), squeeze=False
    )
    axes = axes[0]

    for ax, (N, results) in zip(axes, results_by_N.items()):
        bases = [a for a, _, _ in results]
        outcomes = [o for _, o, _ in results]
        bar_colors = [colors[o] for o in outcomes]
        ax.bar([str(a) for a in bases], [1] * len(bases), color=bar_colors)
        n_success = sum(1 for o in outcomes if o == "success")
        ax.set_title(f"N={N}: {n_success}/{len(outcomes)} valid bases succeeded")
        ax.set_xlabel("base a")
        ax.set_yticks([])
        ax.set_ylim(0, 1.15)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
    fig.legend(
        handles, labels.values(), loc="lower center", ncol=1,
        bbox_to_anchor=(0.5, -0.12), frameon=False,
    )
    fig.suptitle(
        "Shor's algorithm success rate by base a\n"
        "(per-base run_shor_algorithm, no auto-retry across bases)"
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.95])
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    results_by_N = {}
    for N in [15, 21]:
        print(f"\n=== Sweeping N={N} ===", flush=True)
        results_by_N[N] = sweep(N)

    plot_results(results_by_N)

    print("\n=== Summary ===")
    for N, results in results_by_N.items():
        n_success = sum(1 for _, o, _ in results if o == "success")
        n_expected = sum(1 for _, o, _ in results if o == "expected_failure")
        n_unexpected = sum(1 for _, o, _ in results if o == "unexpected_failure")
        print(
            f"N={N}: {n_success}/{len(results)} succeeded, "
            f"{n_expected} expected failures, {n_unexpected} UNEXPECTED failures"
        )
        if n_unexpected:
            print(f"  !! UNEXPECTED FAILURES DETECTED for N={N} - possible bug !!")
