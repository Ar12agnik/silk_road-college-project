from django.shortcuts import render,HttpResponse
import razorpay


# Create your views here.
def paynow(request):
    amount=request.COOKIES['amount']
    email=request.COOKIES['email']
    mobile = request.COOKIES['mobile']
    address=request.COOKIES['address']
    print(address)
    client = razorpay.Client(auth=("rzp_test_NYgixflyiFjkjw", "z6akt2KDr9iPaZhNjdWM8yFZ"))

    data = {"amount": int(amount)*100, "currency": "INR", "receipt": "order_rcptid_11"}
    payment = client.order.create(data=data)

    return render(request,"payment_gateway/paynow.html",context=dict(amount=amount,email=email,mobile=mobile,address=address,payment=payment))
def paynow(request):
    # Check if required cookies exist
    if 'amount' not in request.COOKIES or 'email' not in request.COOKIES or \
       'mobile' not in request.COOKIES or 'address' not in request.COOKIES:
        return HttpResponse("Required information is missing. Please try again.")

    # Extract data from cookies
    amount = int(request.COOKIES['amount'])
    email = request.COOKIES['email']
    mobile = request.COOKIES['mobile']
    address = request.COOKIES['address']

    if amount <= 0:
        return HttpResponse("The order amount must be at least ₹1.")

    # Set up Razorpay client
    client = razorpay.Client(auth=("rzp_test_8LqnCVttuKmh8F", "wEAsiw6baOYd9yGoPoCGgMdp"))

    try:
        # Create Razorpay order
        data = {"amount": amount * 100, "currency": "INR", "receipt": "order_rcptid_11"}
        payment = client.order.create(data=data)
    except razorpay.errors.BadRequestError as e:
        return HttpResponse(f"Payment initiation failed: {e}")

    # Render payment page
    context = {
        "amount": amount,
        "email": email,
        "mobile": mobile,
        "address": address,
        "payment": payment
    }
    return render(request, "payment_gateway/paynow.html", context)
def paynow(request):
    # Check if required cookies exist
    if 'amount' not in request.COOKIES or 'email' not in request.COOKIES or \
       'mobile' not in request.COOKIES or 'address' not in request.COOKIES:
        return HttpResponse("Required information is missing. Please try again.")

    # Extract data from cookies
    amount = int(request.COOKIES['amount'])
    email = request.COOKIES['email']
    mobile = request.COOKIES['mobile']
    address = request.COOKIES['address']

    if amount <= 0:
        return HttpResponse("The order amount must be at least ₹1.")

    # Set up Razorpay client
    client = razorpay.Client(auth=("rzp_test_8LqnCVttuKmh8F", "wEAsiw6baOYd9yGoPoCGgMdp"))

    try:
        # Create Razorpay order
        data = {"amount": amount * 100, "currency": "INR", "receipt": "order_rcptid_11"}
        payment = client.order.create(data=data)
    except razorpay.errors.BadRequestError as e:
        return HttpResponse(f"Payment initiation failed: {e}")

    # Render payment page
    context = {
        "amount": amount,
        "email": email,
        "mobile": mobile,
        "address": address,
        "payment": payment
    }
    return render(request, "payment_gateway/paynow.html", context)