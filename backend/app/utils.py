def sort_stocks_by_gain(stocks: list[dict]) -> list[dict]:
    """
    Sorts a list of stock dictionaries by their percentage gain.
    DSA Practice: Using Python's built-in Timsort via sorted() with a custom lambda key.
    """
    # 1. Filter out stocks missing price or prev_close to avoid DivisionByZero or TypeErrors
    valid_stocks = [s for s in stocks if s.get('price') and s.get('prev_close')]
    
    # 2. Sort using lambda: calculate % gain
    sorted_stocks = sorted(
        valid_stocks, 
        key=lambda x: (x['price'] - x['prev_close']) / x['prev_close'], 
        reverse=True # Descending order: Highest gain first
    )
    
    return sorted_stocks