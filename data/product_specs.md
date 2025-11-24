# Product Specifications - E-Shop Checkout

## Features

### Shopping Cart
- The cart displays a summary of items.
- Initial items: Wireless Headphones ($99.00) and Phone Case ($25.00).
- Base Total: $124.00.

### Discount Codes
- **SAVE15**: Applies a 15% discount to the subtotal (before shipping).
- Invalid codes should display an error message "Invalid code".
- Valid codes should display a success message "15% discount applied!".

### Shipping Options
- **Standard Shipping**: Free ($0.00). Delivery in 5-7 business days.
- **Express Shipping**: Costs $10.00. Delivery in 1-2 business days.
- Changing shipping method updates the total price immediately.

### Payment Methods
- **Credit Card**: Default option.
- **PayPal**: Alternative option.

### User Details Form
- **Full Name**: Required field.
- **Email**: Required field. Must contain '@' symbol.
- **Address**: Required field.

### Order Submission
- Clicking "Pay Now" validates all fields.
- If valid, the form hides and "Payment Successful!" is displayed.
- If invalid, inline error messages are shown for each invalid field.
