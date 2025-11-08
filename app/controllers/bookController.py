from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash

from models.forms import BookForm
from models.users import User
from models.package import Package
from models.book import Booking
from models.bundle import Bundle
from datetime import date, timedelta, datetime
from collections import defaultdict
booking = Blueprint('bookingController', __name__) # use bookingController.fn

@booking.route('/view')
@login_required
def view():
    form = BookForm()
    hotel_name=request.args.get('hotel_name').strip("'")

    the_package_to_be_booked = Package.getPackage(hotel_name=hotel_name)
    print(the_package_to_be_booked)
    return render_template('booking.html', panel=hotel_name, form=form, package=the_package_to_be_booked)




@booking.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        hotel_name=request.form.get("hotel_name")
        check_in_date=request.form.get("check_in_date") 
        # print('check_in_date in book', check_in_date, type(check_in_date))
        # check_in_date in book 2023-03-28 <class 'str'>

        existing_package = Package.getPackage(hotel_name=hotel_name)
        print(existing_package)
        if (current_user is None) or (existing_package is None):
            print(f"Something is wrong")
        elif current_user.email == "admin@abc.com":  
            flash(f"This is a non-admin function. Please log in as a non-admin user to use this function", "info")
            print(f"Admin cannot book package")
        else:
            aBooking = Booking.createBooking(check_in_date, current_user, existing_package) 
            # print('aBooking.check_in_date', aBooking.check_in_date, type(aBooking.check_in_date)) # type is str
            # aBooking.check_in_date 2023-03-28 <class 'str'>
        return redirect(url_for('packageController.packages'))

@booking.route('/manageBooking')
@login_required
def manageBooking(days = -2000):
    bookings = list(Booking.getUserBookingsFromDate(customer=current_user, from_date=date.today()+timedelta(days = days)))
    if bookings:
        bookings.sort(key = lambda b: b.check_in_date)
    return render_template('userBookings.html', panel='Manage Booking', bookings=bookings)

@booking.route("/updateBooking", methods=["POST"])
@login_required
def update():
    hotel_name=request.form.get("hotel_name")
    old_check_in_date=request.form.get("old_check_in_date")
    new_check_in_date=request.form.get("check_in_date")
    # print('old_check_in_date', old_check_in_date, type(old_check_in_date))

    Booking.updateBooking(old_check_in_date, new_check_in_date, current_user, hotel_name)
    return redirect(url_for('bookingController.manageBooking'))
     
@booking.route("/deleteBooking", methods=["POST"])
@login_required
def delete():
    hotel_name=request.form.get("hotel_name")
    check_in_date=request.form.get("old_check_in_date")
    # print(check_in_date, type(check_in_date))
    # convert check_in_date to date type ?? check
    # 2023-03-09 00:00:00 <class 'str'>
    Booking.deleteBooking(check_in_date, current_user, hotel_name)
    return redirect(url_for('bookingController.manageBooking'))

@booking.route('/purchasebundle', methods=['POST'])
@login_required
def purchase_bundle():
    #Bundle.show_all_bundles()
    if current_user.email == 'admin@abc.com':
        flash("This is a non-admin function. Please log in as a non-admin user to use this function", "info")
        return redirect(url_for('packageController.packages'))

    selected = request.form.getlist('selected_packages')

    if not selected:
        flash("Please select packages to buy as a bundle", "info")
        return redirect(url_for('packageController.packages'))

    total_cost = 0
    # bundled_packages = []
    hotel_names = []

    for hotel_id in selected:
        package = Package.getPackage(hotel_id)
        total_cost += package.unit_cost
        hotel_names.append(package.hotel_name)  # Assuming hotel_name is a field

    discount = 0

    if len(selected) >= 4:
        discount = 0.20
    elif len(selected) in [2, 3]:
        discount = 0.10
    discounted_total = total_cost * (1 - discount)

    hotel_list_str = ", ".join(hotel_names)
    if discount == 0:
        flash(f"No discount for bundle {hotel_list_str} <br>Total cost ${total_cost}", "info")
    else: 
        Bundle.createBundle(current_user, [Package.getPackage(hotel_id) for hotel_id in selected])
        flash(f"{int(discount*100)}% discount for bundle purchase {hotel_list_str} <br>Total cost ${total_cost}<br>Discounted total ${discounted_total}", "info")
    return redirect(url_for('packageController.packages'))

@booking.route('/manageBundle')
@login_required
def manage_bundle():
    
    if current_user.email == 'admin@abc.com':
        flash("This is a non-admin function. Please log in as a non-admin user to use this function", "info")
        return redirect(url_for('packageController.packages'))
    #Bundle.show_all_bundles()
    bundles=Bundle.get_bundles_by_customer(current_user).order_by('purchased_date')
    grouped_bundles = defaultdict(list)
    for bundle in bundles:
        grouped_bundles[bundle.purchased_date].append(bundle)

    grouped_bundles = dict(sorted(grouped_bundles.items()))
    #bundles = Bundle.get_all_bundles()
    return render_template('viewbundles.html', panel='Manage Bundle', grouped_bundles=grouped_bundles, today=datetime.utcnow())

@booking.route('/checkin', methods=['POST'])
@login_required
def check_in():
    if current_user.email == 'admin@abc.com':
        flash("This is a non-admin function. Please log in as a non-admin user to use this function", "info")
        return redirect(url_for('packageController.packages'))
    
    package_id = request.form.get("package_id")
    bundle_id = request.form.get("bundle_id")
    # check_in_date = request.form.get("check_in_date")

    Bundle.checkInBundle(bundle_id, package_id, current_user)

    return redirect(url_for('bookingController.manage_bundle'))

