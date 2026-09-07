try:
    # Read input from user
    order_amount = float(input("Enter order amount: "))

    # Apply discount rules
    if order_amount >= 2000:
        discount = 15
    elif order_amount >= 1500:
        discount = 10
    elif order_amount >= 1000:
        discount = 7
    else:
        discount = 0

    # Calculate discount amount
    discount_amount = (order_amount * discount) / 100

    # Final amount after discount
    final_amount = order_amount - discount_amount

    print("Order Amount:", order_amount)
    print("Discount Applied:", discount, "%")
    print("Discount Amount:", discount_amount)
    print("Final Amount:", final_amount)

    # Optional: Add tax
    tax = final_amount * 0.05
    grand_total = final_amount + tax

    print("Tax (5%):", tax)
    print("Grand Total:", grand_total)

except ValueError:
    print("Error: Please enter a valid numeric value.")