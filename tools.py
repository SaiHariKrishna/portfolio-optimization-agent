from risk_metrics import modified_duration
from optimizer import optimize_weights

def duration_tool(bond):
    return modified_duration(
        face=float(bond["face_value"]),
        coupon=float(bond["coupon"]),
        maturity=int(bond["maturity_years"]),
        yield_rate=float(bond["market_yield"])
    )

def optimization_tool(durations, target_duration):
    return optimize_weights(durations, target_duration)
