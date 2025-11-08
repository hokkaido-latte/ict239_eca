from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app import db
from models.book import Booking

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/trend_chart', methods=['GET', 'POST'])
@login_required
def trend_chart():
    if current_user.email != "admin@abc.com":
        return "Access denied. Admins only.", 403
    else:
        if request.method == 'GET':
            return render_template('trend_chart.html', panel="Package Chart")
    
        elif request.method == 'POST':
            chart_type = request.form.get('chart_type', 'amount_incoming')
            all_bookings = Booking.getAllBookings()
            print(f"There are {len(all_bookings)} of booking records")

            if chart_type == 'amount_incoming':
                # Process amount incoming data
                hotel_costbyDate = {}

                for aBooking in list(all_bookings):
                    hotel_name = aBooking.package.hotel_name
                    check_in_date = aBooking.check_in_date
                      
                    if hotel_name not in hotel_costbyDate:
                        hotel_costbyDate[hotel_name] = {}
                    if check_in_date not in hotel_costbyDate[hotel_name]:
                        hotel_costbyDate[hotel_name][check_in_date] = 0
                    hotel_costbyDate[hotel_name][check_in_date] += aBooking.total_cost
        
                hotel_costbyDateSortedListValues = {}
                for hotel, dateAmts in hotel_costbyDate.items():
                    hotel_costbyDateSortedListValues[hotel] = sorted(list(dateAmts.items()))

                print("Sending Amount Incoming data:", hotel_costbyDateSortedListValues)
                return jsonify({'chartDim': hotel_costbyDateSortedListValues, 'labels': [], 'chartType': 'line'})

            elif chart_type == 'bookings_by_month':
                month_hotel_bookings = {}
    
                for aBooking in list(all_bookings):
                    hotel_name = aBooking.package.hotel_name
                    check_in_date = aBooking.check_in_date
        
                    month_year = check_in_date.strftime("%B %Y")
        
                    if month_year not in month_hotel_bookings:
                        month_hotel_bookings[month_year] = {}
                    if hotel_name not in month_hotel_bookings[month_year]:
                        month_hotel_bookings[month_year][hotel_name] = 0
                    month_hotel_bookings[month_year][hotel_name] += 1  # Count bookings
    
                all_hotels = set()
                for month_data in month_hotel_bookings.values():
                    all_hotels.update(month_data.keys())
                all_hotels = sorted(list(all_hotels))
    
                all_months = sorted(list(month_hotel_bookings.keys()), 
                                   key=lambda x: datetime.strptime(x, "%B %Y"))
    
                month_bookings_data = {}
                for month in all_months:
                    month_data = []
                    for hotel in all_hotels:
                        count = month_hotel_bookings[month].get(hotel, 0)
                        month_data.append([hotel, count])  # [hotel_name, booking_count]
                    month_bookings_data[month] = month_data
    
                print("Sending Bookings By Month data:", month_bookings_data)
                return jsonify({
                    'chartDim': month_bookings_data, 
                    'labels': all_hotels,  # Hotel names for x-axis
                    'chartType': 'bar'
                })