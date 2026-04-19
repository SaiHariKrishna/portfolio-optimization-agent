try:
    import QuantLib as ql
    _HAS_QL = True
except ImportError:
    _HAS_QL = False

def modified_duration(face, coupon, maturity, yield_rate):
    if not _HAS_QL:
        raise ImportError("QuantLib is required for modified_duration. pip install QuantLib")
    face = float(face)
    coupon = float(coupon)
    yield_rate = float(yield_rate)

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today

    maturity_date = today + int(365 * maturity)

    schedule = ql.Schedule(
        today,
        maturity_date,
        ql.Period(ql.Annual),
        ql.NullCalendar(),
        ql.Unadjusted,
        ql.Unadjusted,
        ql.DateGeneration.Forward,
        False
    )

    day_count = ql.ActualActual(ql.ActualActual.ISDA)

    bond = ql.FixedRateBond(
        0,
        face,
        schedule,
        [coupon],   # now guaranteed clean
        day_count
    )

    ytm = ql.InterestRate(
        yield_rate,
        day_count,
        ql.Compounded,
        ql.Annual
    )

    return ql.BondFunctions.duration(
        bond, ytm, ql.Duration.Modified
    )


def bond_convexity(face, coupon, maturity, yield_rate):
    """Calculate bond convexity using analytical formula (pure numpy).

    Convexity = (1/P) * sum[ t*(t+1)*CF / (1+y)^(t+2) ]
    """
    face = float(face)
    coupon = float(coupon)
    yield_rate = float(yield_rate)
    maturity = int(maturity)

    annual_coupon = face * coupon
    y = yield_rate

    # Calculate price
    price = 0.0
    for t in range(1, maturity + 1):
        cf = annual_coupon + (face if t == maturity else 0.0)
        price += cf / (1 + y) ** t

    if price <= 0:
        return 0.0

    # Calculate convexity
    convexity_sum = 0.0
    for t in range(1, maturity + 1):
        cf = annual_coupon + (face if t == maturity else 0.0)
        convexity_sum += t * (t + 1) * cf / (1 + y) ** (t + 2)

    return convexity_sum / price
