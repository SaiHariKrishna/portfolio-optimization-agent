import QuantLib as ql

def modified_duration(face, coupon, maturity, yield_rate):
    face = float(face)
    coupon = float(coupon)
    yield_rate = float(yield_rate)

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today

    # Ensure maturity is at least 1 day in the future
    days_to_maturity = max(1, int(365 * maturity))
    maturity_date = today + days_to_maturity

    # For very short-term instruments (like BIL), use a smaller frequency
    frequency = ql.Annual
    if maturity < 1.0:
        frequency = ql.Semiannual # Flexible for short term
        
    schedule = ql.Schedule(
        today,
        maturity_date,
        ql.Period(frequency),
        ql.NullCalendar(),
        ql.Unadjusted,
        ql.Unadjusted,
        ql.DateGeneration.Backward, # Backward logic is more robust for short durations
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
