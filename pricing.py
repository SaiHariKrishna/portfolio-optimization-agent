import QuantLib as ql

def price_bond(face, coupon, maturity, yield_rate):
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
        [coupon],
        day_count
    )

    curve = ql.FlatForward(today, yield_rate, day_count)
    engine = ql.DiscountingBondEngine(
        ql.YieldTermStructureHandle(curve)
    )

    bond.setPricingEngine(engine)
    return bond.cleanPrice()