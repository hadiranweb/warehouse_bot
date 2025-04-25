def validate_quantity(quantity):
    try:
        qty = int(quantity)
        if qty <= 0:
            raise ValueError("تعداد باید مثبت باشد!")
        return qty
    except ValueError:
        raise ValueError("تعداد باید عدد باشد!")
