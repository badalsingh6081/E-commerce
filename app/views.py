from django.shortcuts import render,redirect
from django.views import View
from .models import Customer,Cart,Product,OrderPlaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse 
from  django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator





class ProductView(View):
   def get(self,request):
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    topwears=Product.objects.filter(category='TW')
    bottomwears=Product.objects.filter(category='BW')
    mobiles=Product.objects.filter(category='M')
    cosmetics=Product.objects.filter(category='CM')
    electronics=Product.objects.filter(category='EL')
    return render(request,'app/home.html',{'topwears':topwears,'bottomwears':bottomwears,'mobiles':mobiles,'electronics':electronics,'cosmetics':cosmetics ,'totalitem':totalitem})



class ProductDetailView(View):
    def get(self,request,pk):
     product=Product.objects.get(pk=pk)
     item_already_in_cart=False
     if request.user.is_authenticated:
         item_already_in_cart=Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
         totalitem=0
         totalitem=len(Cart.objects.filter(user=request.user))

     return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})



@login_required
def add_to_cart(request):
 user=request.user
 product_id=request.GET.get('prod_id')
 product=Product.objects.get(id=product_id)
 cart=Cart(user=user,product=product )
 cart.save()
 return redirect('/show-cart/')


@login_required
def show_cart(request):
  if request.user.is_authenticated:
    user=request.user
    cart=Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=70.0
    total_amount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user==user ]
    if cart_product:
      for p in cart_product:
        tempamount=(p.quantity*p.product.discounted_Price)
        amount+=tempamount
      total_amount=amount+shipping_amount
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))  
      return render(request, 'app/addtocart.html',{'carts':cart,'total_amount':total_amount,'amount':amount,'totalitem':totalitem}) 
    else:
      return render(request,'app/emptycart.html ')

 
@login_required
def plus_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity +=1
    c.save()
    amount=0.0
    shipping_amount=70.0
    cart_product=[p for p in Cart.objects.all() if p.user== request.user ]
    if cart_product:
      for p in cart_product:
        tempamount=(p.quantity*p.product.discounted_Price)
        amount+=tempamount
  
    data={
      'quantity':c.quantity,
      'amount':amount,
      'totalamount': amount+shipping_amount
    }
    return JsonResponse(data)
  
@login_required
def minus_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.quantity -=1
    c.save()
    amount=0.0
    shipping_amount=70.0
    cart_product=[p for p in Cart.objects.all() if p.user== request.user ]
    if cart_product:
      for p in cart_product:
        tempamount=(p.quantity*p.product.discounted_Price)
        amount+=tempamount
    data={
      'quantity':c.quantity,
      'amount':amount, 
      'totalamount': amount+shipping_amount
    }
    return JsonResponse(data)

@login_required
def remove_cart(request):
  if request.method=='GET':
    prod_id=request.GET['prod_id']
    c=Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
    c.delete()
    amount=0.0
    shipping_amount=70.0
    
    cart_product=[p for p in Cart.objects.all() if p.user== request.user ]
    if cart_product:
      for p in cart_product:
        tempamount=(p.quantity*p.product.discounted_Price)
        amount+=tempamount
      
    data={
      'amount':amount, 
      'totalamount': amount+shipping_amount
    }
    return JsonResponse(data)




@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')


@login_required
def address(request):
 add=Customer.objects.filter(user=request.user)
 totalitem=0
 if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user)) 
 return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

@login_required 
def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})




def mobile(request,data=None):
    if data==None:
        mobiles=Product.objects.filter(category='M')
    elif data=='Iphone' or data=='Samsung':
        mobiles=Product.objects.filter(category='M').filter(brand=data)
    elif data=='below':
        mobiles=Product.objects.filter(category='M').filter(discounted_Price__lt=10000)
    elif data=='above':
        mobiles=Product.objects.filter(category='M').filter(discounted_Price__gt=10000)
    
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'app/mobile.html',{'mobiles':mobiles,'totalitem':totalitem})




class CustomerRegistrationView(View):
  def get(self,request):
    form= CustomerRegistrationForm()
    return render(request,'app/customerregistration.html',{'form':form})
  def post(self,request):
    form=CustomerRegistrationForm(request.POST)
    if form.is_valid():
      messages.success(request,'Congratulations!! Registered Successfully')
      form.save()
    return render(request,'app/customerregistration.html',{'form':form})
      




@login_required
def checkout(request):
    user=request.user
    add = Customer.objects.filter(user=user)
    cart_items=Cart.objects.filter(user=request.user)

    amount = 0.0
    shipping_amount=70.0
    totalamount=0.0
    cart_product=[p for p in Cart.objects.all() if p.user== request.user ]
    if cart_product:
      for p in cart_product:
        tempamount=(p.quantity*p.product.discounted_Price)
        amount+=tempamount
      totalamount=amount+shipping_amount 
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user)) 
    return render(request, 'app/checkout.html',{'cart_items':cart_items,'add':add,'total_amount':totalamount,'totalitem':totalitem,})







@method_decorator(login_required,name='dispatch')
class ProfileView(View):
  def get(self,request):
    form=CustomerProfileForm()
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user)) 
    
    return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})
  def post(self,request):
    form=CustomerProfileForm(request.POST)
    if form.is_valid():
      user=request.user
      name=form.cleaned_data['name']
      locality=form.cleaned_data['locality']
      city=form.cleaned_data['city']
      state=form.cleaned_data['state']
      zipcode=form.cleaned_data['zipcode']
      reg=Customer(user=user,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
      reg.save()
      messages.success(request,'Congratulations!! Profile Updated Successfully')
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})




    # ==========================================================================

# views for payment    
from django.shortcuts import get_object_or_404  
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse

def process_payment(request):
    # if request.method == 'GET':
    custid = request.GET.get('custid')
    total_amount = request.GET.get('total_amount') 
    
    c=Cart.objects.filter(user=request.user)
    for o in c:
      order_id=[]
      order_quantity=[]
      i=0
      order_id.append(o.id)
      order_quantity.append(o.quantity)
      i+=i
      # print('product_id',order_id[0],"produuct_quantity", order_quantity[0])
    host = request.get_host()


    paypal_dict = {
           'business': settings.PAYPAL_RECEIVER_EMAIL,
           'amount': total_amount,
           # 'amount': '%.2f' % total_amount.quantize(
           #     Decimal('.01')),
           'item_name': 'Order{}'.format(order_id[0]),
           'invoice': str(order_id[0]),
           'currency_code': 'USD',
           'notify_url': 'http://{}{}'.format(host,
                                              reverse('paypal-ipn')),
           'return_url': 'http://{}{}'.format(host,
                                              reverse('payment_done',args=custid)),
           'cancel_return': 'http://{}{}'.format(host,
                                                 reverse('payment_cancelled')),
       }

    form = PayPalPaymentsForm(initial=paypal_dict)
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/process_payment.html', {'form': form,'totalitem':totalitem})






# @csrf_exempt
def payment_done(request,id):
    user=request.user
    customer = Customer.objects.get(id=id)
    cart = Cart.objects.filter(user=user)
    for c in cart:
      OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
      c.delete()
    totalitem=0
    if request.user.is_authenticated:
      totalitem=len(Cart.objects.filter(user=request.user))
    return render(request, 'app/payment_success.html',{'totalitem':totalitem})
 
    # return redirect('/orders/')  

# @csrf_exempt
def payment_canceled(request):
    return render(request, 'app/payment_failed.html')