from django.shortcuts import render, redirect, reverse, get_object_or_404
from . import forms, models
from .models import Product
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
import random
def dev_vendors(request):
    return redirect("https://www.devvendors.online/")

def home_view(request,):
    products = models.Product.objects.all()
    products = list(products)
    random.shuffle(products)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'ecom/index.html', {'products': products, 'product_count_in_cart': product_count_in_cart})


# for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)
        username = request.POST.get('username')  # Adjust based on your actual form field
        if User.objects.filter(username=username).exists():
            # Add appropriate handling for existing user (e.g., show an error message)
            messages.error(request, 'Username already exists. Please choose a different one.')
            return render(request, 'ecom/customersignup.html', context=mydict)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
            name = str(request.POST.get('first_name')) + " " + str(request.POST.get("last_name"))
            print(name)
            EMAIL_RECEIVING_USER = request.POST.get('email', None)
            if EMAIL_RECEIVING_USER is None:
                print("Error!!")
            message = ("Welcome to Silk Road We're excited to see you here!! check out our Latest offers click "
                       "here(domain_name.com)\n please Do not reply to this mail!")
            try:
                send_mail("Greetings!" + str(name), message, settings.EMAIL_HOST_USER, [str(EMAIL_RECEIVING_USER)],
                        fail_silently=True)
                message = f"A {name} Just with email adress {EMAIL_RECEIVING_USER} Registered in your website "
                send_mail("Greetings! Admin", message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER,
                        fail_silently=True)
            except:
                pass
        return HttpResponseRedirect('customerlogin')
    return render(request, 'ecom/customersignup.html', context=mydict)


# -----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


# ---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')


# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount = models.Customer.objects.all().count()
    productcount = models.Product.objects.all().count()
    ordercount = models.Orders.objects.all().count()

    # for recent order tables
    orders = models.Orders.objects.all()
    ordered_products = []
    ordered_bys = []
    for order in orders:
        ordered_product = models.Product.objects.all().filter(id=order.product.id)
        ordered_by = models.Customer.objects.all().filter(id=order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict = {
        'customercount': customercount,
        'productcount': productcount,
        'ordercount': ordercount,
        'data': zip(ordered_products, ordered_bys, orders),
    }
    return render(request, 'ecom/admin_dashboard.html', context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers = models.Customer.objects.all()
    return render(request, 'ecom/view_customer.html', {'customers': customers})


# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return redirect('view-customer')
    return render(request, 'ecom/admin_update_customer.html', context=mydict)


# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products = models.Product.objects.all()
    return render(request, 'ecom/admin_products.html', {'products': products})


# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request, 'ecom/admin_add_products.html', {'productForm': productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    productForm = forms.ProductForm(instance=product)
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
        else:
            print("save not performed!!")
    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})


def update_product_view(request, pk):
    product = models.Product.objects.get(id=pk)
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES, instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
        else:
            print(productForm.errors)  # Add this line to print form errors for debugging
    else:
        productForm = forms.ProductForm(instance=product)

    return render(request, 'ecom/admin_update_product.html', {'productForm': productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders = models.Orders.objects.all()
    ordered_products = []
    ordered_bys = []
    for order in orders:
        ordered_product = models.Product.objects.all().filter(id=order.product.id)
        ordered_by = models.Customer.objects.all().filter(id=order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request, 'ecom/admin_view_booking.html', {'data': zip(ordered_products, ordered_bys, orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')


# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request, pk):
    order = models.Orders.objects.get(id=pk)
    orderForm = forms.OrderForm(instance=order)
    if request.method == 'POST':
        orderForm = forms.OrderForm(request.POST, instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request, 'ecom/update_order.html', {'orderForm': orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks = models.Feedback.objects.all().order_by('-id')
    return render(request, 'ecom/view_feedback.html', {'feedbacks': feedbacks})


# ---------------------------------------------------------------------------------
# ------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
# ---------------------------------------------------------------------------------




def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET.get('query','')
    print(type(query))
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    print(products)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # word variable will be shown in html when user click on search button
    word = "Searched Result :"

    if request.user.is_authenticated:
        return render(request, 'ecom/customer_home.html',
                      {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})
    return render(request, 'ecom/index.html',
                  {'products': products, 'word': word, 'product_count_in_cart': product_count_in_cart})


#show product discription
def product_detail(request,pk):
    try:
        product= Product.objects.get(id=pk)
        return render(request,'ecom/product_detail.html',{'products':product})
    except Exception as e:
        print(e)
        return render(request,'ecom/oops_page.html')
        
# any one can add product to cart, no need of signin
def add_to_cart_view(request, pk):
    products = models.Product.objects.all()

    # for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']

        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 1

    response = render(request, 'ecom/index.html',
                      {'products': products, 'product_count_in_cart': product_count_in_cart})

    # adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        old_qty = request.COOKIES['quantity']
        # quantity = request.COOKIES['quantity']
        if product_ids == "":
            product_ids = str(pk)
            quant_val = 1
            quantity = f"{product_ids} + {quant_val}"
        else:
            product_ids = product_ids + "|" + str(pk)
            quant_val = 1
            quantity = f"{product_ids} + {quant_val}|{old_qty}"
        response.set_cookie('product_ids', product_ids)
        response.set_cookie("quantity", quantity)
        # quant_val=1
        # quantity=f"{product_ids}+{quant_val}| {old_qty}"
    else:
        quant_val = 1
        quantity = f"{pk} + {quant_val}"
        response.set_cookie('product_ids', pk)
        response.set_cookie("quantity", quantity)

    # product = models.Product.objects.get(id=pk)
    # messages.info(request, product.name + ' added to cart successfully!')

    return response


# for checkout of cart
def cart_view(request):
    if request.user.is_authenticated:
        auth=True
    else:
        auth=False
    quantity_html = []
    total = 0
    already_added_prods = []
    products = []

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        quantity = request.COOKIES['quantity']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            quantity_in_cart = quantity.split('|')
            if quantity_in_cart[-1] == '':
                quantity_in_cart.pop()
            qp = [j.split('+') for j in quantity_in_cart]

            products = models.Product.objects.filter(id__in=product_id_in_cart)

            for p in products:
                for i in qp:
                    if i == '':
                        continue
                    if int(i[0]) == p.id and len(i) > 1 and i[0] not in already_added_prods:
                        total += p.price * int(i[1])
                        already_added_prods.append(i[0])
                        quantity_html.append({'id': int(i[0]), 'quantity': int(i[1]), 'price': p.price})

    quantity_html.sort(key=lambda x: x['id'])
    product_count_in_cart = len(set(already_added_prods))

    if request.method == 'POST':
        updated_quantity = int(request.POST.get("quantity", 0))
        pid = int(request.POST.get("pid", 0))

        for prod in quantity_html:
            if prod['id'] == pid:
                temp = prod['quantity']
                prod['quantity'] = updated_quantity
                prod['price'] = models.Product.objects.get(id=pid).price * updated_quantity
                total += prod['price'] - (temp * models.Product.objects.get(id=pid).price)

        # Update the quantity in the cookie
        quantity_cookie = '|'.join([f"{prod['id']}+{prod['quantity']}" for prod in quantity_html])
        response = redirect('cart')
        response.set_cookie("quantity", quantity_cookie)
        response.set_cookie("quantity_html", quantity_html)
        return response
    print("quantity_html=", quantity_html)

    return render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'product_count_in_cart': product_count_in_cart,
        'quantity': quantity_html,'auth':auth
    })

def remove_from_cart_view(request, pk):
    # for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    # removing product id from cookie
    total = 0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart = product_ids.split('|')
        product_id_in_cart = list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products = models.Product.objects.all().filter(id__in=product_id_in_cart)
        # for total price shown in cart after removing product
        for p in products:
            total = total + p.price

        #  for update coookie value after removing product id in cart
        value = ""
        for i in range(len(product_id_in_cart)):
            if i == 0:
                value = value + product_id_in_cart[0]
            else:
                value = value + "|" + product_id_in_cart[i]
        response = render(request, 'ecom/removed_from_cart.html',
                          {'products': products, 'total': total, 'product_count_in_cart': product_count_in_cart})
        if value == "":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids', value)
        return response
    


def send_feedback_view(request):
    feedbackForm = forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm': feedbackForm})


# ---------------------------------------------------------------------------------
# ------------------------ CUSTOMER RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products = models.Product.objects.all()
    products = list(products)
    random.shuffle(products)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0
    return render(request, 'ecom/customer_home.html',
                  {'products': products, 'product_count_in_cart': product_count_in_cart})

def orders_return(request):
    if request.method=='POST':
        Pname=request.POST.get('pname',None)
        Cphone=request.POST.get('cphone',None)
        dop=request.POST.get('dop',None)
        caddress=request.POST.get('caddress',None)
        user_name=request.user.first_name+' '+request.user.last_name
        if Pname  or Cphone or dop or caddress or user_name is not None:
            return_order=models.returnorder(Pname=Pname,user_name=user_name,caddress=caddress,Cphone=Cphone,dop=dop)
            return_order.save()
            message=f"{user_name} wants to return the order {Pname} the mentioned address {caddress}"
            try:
                send_mail("return order request!!",message,settings.EMAIL_HOST_USER,settings.EMAIL_HOST_USER)
            except:
                pass
            return redirect(reverse('home'))
    return render(request,"ecom/orders_return.html")
# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart = False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart = True
    # for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(set(counter))
    else:
        product_count_in_cart = 0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            # for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total = 0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                quantity=request.COOKIES['quantity']
                if product_ids != "":
                    product_id_in_cart = product_ids.split('|')
                    quantity_id_in_cart = quantity.split('|')
                    print(quantity_id_in_cart)
                    products = models.Product.objects.all().filter(id__in=product_id_in_cart)
                    for p in products:
                        for q in quantity_id_in_cart:
                            q=q.split("+")
                            if int(q[0]) == int(p.id):
                                if len(q) > 1:
                                    total = total + p.price*int(q[1])

            response = redirect("/pay_now")#render(request, 'ecom/payment.html', {'total': total})
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            response.set_cookie("amount", total)

            return response
    return render(request, 'ecom/customer_address.html',
                  {'addressForm': addressForm, 'product_in_cart': product_in_cart,
                   'product_count_in_cart': product_count_in_cart})
def buy_now(request,pk):
    response = redirect('customer-address')
    response.set_cookie('product_ids', pk)
    quantity=f"{pk} + {1}"
    response.set_cookie("quantity", quantity)
    return response


# here we are just directing to this view...actually we have to check whther payment is successful or not
# then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer = models.Customer.objects.get(user_id=request.user.id)
    products = None
    email = None
    mobile = None
    address = None
    if 'product_ids' in request.COOKIES:
        quantity = request.COOKIES['quantity']
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart = product_ids.split('|')
            quantity_in_cart = quantity.split('|')
            # quantity_in_cart = quantity_in_cart.split('+')
            print(quantity_in_cart)
            print(product_id_in_cart)
            products = models.Product.objects.all().filter(id__in=product_id_in_cart)
            print(products)

            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email = request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']
    checker = 0
    p_n = ''
    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    razorpay_signature=request.GET.get('razorpay_signature',None)
    razorpay_order_id=request.GET.get('razorpay_order_id',None)
    razorpay_payment_id=request.GET.get('razorpay_payment_id',None)
    print("*********************")
    print("razorpay_signature",razorpay_signature)
    print("razorpay_order_id",razorpay_order_id)
    print("razorpay_payment_id",razorpay_payment_id)
    print("*********************")

    for product in products:
        for quantity in quantity_in_cart:
            quantity = quantity.split("+")
            if len(quantity)==2:
                qty=int(quantity[1])
            else:
                continue
            if product.id == int(quantity[0]):
                models.Orders.objects.get_or_create(customer=customer, product=product, status='Pending', email=email,
                                                    mobile=mobile, address=address, quantity=qty,razorpay_payment_id=razorpay_payment_id,razorpay_order_id=razorpay_order_id,razorpay_signature=razorpay_signature)
                if (product.quantity - int(quantity[1])) >= 0:
                    product.quantity = product.quantity - int(quantity[1])
                    product.save()
                    p_n += f"{product.name} "
                    if product.quantity<2:
                        try:
                            send_mail(f"product {product.name} is out of Stalk!!",
                                  f"Dear Admin,\n your product named {product.name} has alarmingly Low Quantity!! Please refill it! \nProduct name: {product.name}\n Product id: {product.id}\n Product Description: {product.description}\nPrice: {product.price}",settings.EMAIL_HOST_USER,settings.EMAIL_RECEIVING_USER,fail_silently=True)
                        except:
                            pass


                else:
                    try:
                        send_mail(f"{product.name} is Currently out of stalk",
                              f"Sorry but your Shipment of the product {product.name} might get delayed due to lack of stalk\n we are trying Our best to bring the product to stalk at earliest!! \n The rest of the products will reach you in Time! For any doubts/quearies please contact {settings.EMAIL_HOST_USER} or the Mobile Number {settings.MOBILE}",settings.EMAIL_HOST_USER, [email,], fail_silently=True)
                    except:
                        pass
                    checker+=1
                    try:
                        send_mail(f"product {product.name} is out of Stalk!!",f"Dear Admin,\n your product named {product.name} is out of stalk \nProduct name: {product.name}\n Product id: {product.id}\n Product Description: {product.description}\nPrice: {product.price}",settings.EMAIL_HOST_USER,settings.EMAIL_RECEIVING_USER,fail_silently=True)
                    except:
                        pass
    if checker == 0:
        try:
            send_mail(f"Order Placed!!",
                  f"Your order for {p_n} is successfully Placed!\n Thankyou for shopping With Us! \n click here -> domainname.com to get more offers!!",
                  settings.EMAIL_HOST_USER,[email,], fail_silently=True)
        except:
            pass
        checker += 1

    # after order placed cookies should be deleted
    response = render(request, 'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    orders = models.Orders.objects.all().filter(customer_id=customer)
    ordered_products = []
    for order in orders:
        ordered_product = models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request, 'ecom/my_order.html', {'data': zip(ordered_products, orders)})


# @login_required(login_url='customerlogin')
# @user_passes_test(is_customer)
# def my_order_view2(request):

#     products=models.Product.objects.all()
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0
#     return render(request,'ecom/my_order.html',{'products':products,'product_count_in_cart':product_count_in_cart})


# --------------for discharge patient bill (pdf) download and printing
import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    order = models.Orders.objects.get(id=orderID)
    product = models.Product.objects.get(id=productID)
    mydict = {
        'orderDate': order.order_date,
        'customerName': request.user,
        'customerEmail': order.email,
        'customerMobile': order.mobile,
        'shipmentAddress': order.address,
        'orderStatus': order.status,
        "transactionId":order.razorpay_payment_id,
        "quantity": order.quantity,
        "total":product.price*int(order.quantity),

        'productName': product.name,
        'productImage': product.product_image,
        'productPrice': product.price,
        'productDescription': product.description,


    }
    return render_to_pdf('ecom/download_invoice.html', mydict)


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    return render(request, 'ecom/my_profile.html', {'customer': customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    user = models.User.objects.get(id=customer.user_id)
    userForm = forms.CustomerUserForm(instance=user)
    customerForm = forms.CustomerForm(request.FILES, instance=customer)
    mydict = {'userForm': userForm, 'customerForm': customerForm}
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request, 'ecom/edit_profile.html', context=mydict)


# ---------------------------------------------------------------------------------
# ------------------------ ABOUT US AND CONTACT US VIEWS START --------------------
# ---------------------------------------------------------------------------------
def aboutus_view(request):
    return render(request, 'ecom/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            try:
                send_mail(str(name) + ' || ' + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER,fail_silently=True)
            except:
                pass
            return render(request, 'ecom/contactussuccess.html')
    return render(request, 'ecom/contactus.html', {'form': sub})
def log_out(request):
    logout(request)
    return redirect('home')