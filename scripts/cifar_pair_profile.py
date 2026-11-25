"""Endpoint of the symmetric two-atom continuation after a CIFAR handoff."""
import math

from scipy.integrate import solve_ivp


def classify_profile(q, tau, radius, w, bias):
    """Return (mid/+/-/unresolved, stopping reason) for a projected state.

    In phase coordinates L = r*(exp(tau)-1), s = L*exp(tau)*q,
    ds/dL = s/L + L*F(s). The boundaries are evaluated on |s| by symmetry.
    """
    if not (math.isfinite(q) and math.isfinite(tau)):
        return "unresolved", "nonfinite handoff"
    if q == 0:
        return "mid", "symmetry"
    atom = "+" if q > 0 else "-"
    threshold = 1 / math.sinh(bias)**2
    if w <= threshold:
        return atom, "subcritical"
    outer = math.acosh(math.sqrt(w / threshold))
    start = radius * math.expm1(tau)
    s0 = abs(q) * math.exp(tau) * start
    if s0 >= outer:
        return atom, "outer barrier"

    sinh2 = math.sinh(bias)**2

    def field(s):
        # The expression tends to +/-1 outside the transition layer.
        inv_cosh2 = 1 / math.cosh(min(abs(s), 350))**2
        return math.tanh(s) * (1 - w*sinh2*inv_cosh2) / (1 + sinh2*inv_cosh2)

    def inward(level, s):
        return s + level**2 * field(s)

    if inward(start, s0) < 0:
        return "mid", "inward barrier"

    # Follow z = s/L up to the first barrier. At s = outer the flow
    # points outwards. At inward = 0 with F(s)<0 the flow turns inwards:
    # at that fixed wall the inward inequality then strengthens with L.
    def turn(level, z):
        return inward(level, level * z[0])

    def escape(level, z):
        return level * z[0] - outer

    turn.terminal, turn.direction = True, -1
    escape.terminal, escape.direction = True, 1

    def resolve(tol):
        end = max(2 * start, 2.0)
        level, z = start, [abs(q) * math.exp(tau)]
        for _ in range(15):
            solution = solve_ivp(lambda x, y: [field(x * y[0])], (level, end), z,
                                 method="DOP853", events=(turn, escape), rtol=tol,
                                 atol=tol * abs(z[0]) * 0.01)
            if not solution.success:
                return "unresolved"
            if solution.t_events[0].size:
                return "mid"
            if solution.t_events[1].size:
                return atom
            level, z = end, solution.y[:, -1]
            end *= 2
        return "unresolved"

    first = resolve(1e-8)
    second = resolve(1e-10)
    if first == second and first != "unresolved":
        return first, "profile event"
    return "unresolved", "inconclusive profile integration"
