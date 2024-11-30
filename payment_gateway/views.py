from django.shortcuts import render
import razorpay


# Create your views here.
def paynow(request):
    amount=request.COOKIES['amount']
    email=request.COOKIES['email']
    mobile = request.COOKIES['mobile']
    address=request.COOKIES['address']
    print(address)
    client = razorpay.Client(auth=("rzp_test_8LqnCVttuKmh8F", "wEAsiw6baOYd9yGoPoCGgMdp"))

    data = {"amount": int(amount)*100, "currency": "INR", "receipt": "order_rcptid_11"}
    payment = client.order.create(data=data)

    return render(request,"payment_gateway/paynow.html",context=dict(amount=amount,email=email,mobile=mobile,address=address,payment=payment))