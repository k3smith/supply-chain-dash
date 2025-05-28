from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import forms 
import folium
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import io, requests
import urllib, base64
from datetime import datetime, timedelta, timezone
import calendar
import os
from dotenv import load_dotenv

load_dotenv()

from mainDash.static.mainDash.color_data import industry_info, naics_industry
from mainDash.static.mainDash.commodity_data import commodity_series_mapping

from .models import Item, SupplierItem, Supplier, Coordenadas

def index(request, item_id=None, sort_by="date_req"):
    template = loader.get_template("mainDash/index.html")

    # Bill of materials information
    n = 10
    if sort_by == "date_req":
        latest_BOM = Item.objects.order_by(sort_by)[:n]
    else :
        latest_BOM = Item.objects.order_by('-'+sort_by)[:n]
    supplierCounts = []
    for item in latest_BOM.all().values() :
        supplierCounts.append(Supplier.objects.filter(naics_code=item['naics_code']).count())
    
    # Map information 
    if item_id == None or item_id == -1 :
        coordenadas = list(Coordenadas.objects.values_list('lat','lon'))
        suppliers = Supplier.objects.all().values()
    else :
        naics_code = Item.objects.filter(id=item_id).values_list('naics_code')[0][0]
        suppliers = Supplier.objects.filter(naics_code=naics_code).all().values()
    
    if len(suppliers) > 0 :
        map = folium.Map(location=[39.828, -98.579],
                        zoom_start=3.5,
                        control_scale=True)
        for supplier in suppliers :
            c = Coordenadas.objects.filter(supplier_id=supplier['id']).all().values()[0]
            p_text = '<strong>' + supplier['supplier_name'] + '<strong> <br> Quality: ' + str(supplier['quality']) + '<br> Delay Risk: ' + str(supplier['delay_risk'])
            #str(text_format.BOLD) + supplier['supplier_name'] + str(text_format.END) + '\n' 'Quality: ' + str(supplier['quality']) + '\n' 'Delay Risk: ' + str(supplier['delay_risk'])
            folium.Marker(location=[c['lat'], c['lon']], icon=folium.Icon(color=industry_info[supplier['naics_code']]['color'], icon=industry_info[supplier['naics_code']]['icon'], prefix="fa"), popup=p_text).add_to(map)
        folium.raster_layers.TileLayer('Stamen Terrain').add_to(map)
    else :
        map = folium.Map([39.828, -98.579], zoom_start=4)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(map)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(map)
    folium.LayerControl().add_to(map)

    map = map._repr_html_()

    # Map legend
    legend_items = []
    for key, value in industry_info.items():
        legend_item = f"""        
       <i class="fa-solid {value['icon']}" style="background-color: {value['color']}; color: #ffffff; padding: 5px; width: 20px; height: 20px"></i>
            {naics_industry[key]} <br>
        """
        legend_items.append(legend_item)

    # Combine the legend items into a single HTML content
    legend_html = f"""
    <head>
            <script src="https://kit.fontawesome.com/963475e21a.js" crossorigin="anonymous"></script>
    </head>
    <div class="legend">
        {''.join(legend_items)}
    </div>
    """

    context = {
        "map":map,
        "legend":legend_html,
        "latest_BOM": zip(latest_BOM, supplierCounts)
    }
    
    return HttpResponse(template.render(context, request))

def detail(request):
    template = loader.get_template("mainDash/detail.html")
    selected_item_ids = request.GET.getlist('selected_items')
    selected_items = Item.objects.filter(id__in=selected_item_ids)
    
    # Define the start and end dates
    start_date = datetime.now()
    start_date = start_date.replace(tzinfo=timezone.utc)
    date_list = [x[0] for x in selected_items.values_list('date_req').all()]
    print(date_list)
    end_date = max(date_list)

    # Generate the list of month-year dates
    potential_dates = generate_month_year_dates(start_date, end_date)

    # Generate planned order schedule: DEFAULT
    items = {}
    for i in selected_items.values().all() :
        items[i['id']] = {i['date_req'].strftime('%b %Y'): {
            'quantity': i['quantity']
        }}

    table_body = ''
    for i in selected_items.values().all() :
        table_body += f"""<tr><td>""" + str(i['item_description']) + f"""</td>
                <td class="item-quantity">""" + str(i['quantity']) + f"""</td>
                <td>""" + str(i['criticality']) + f"""</td>
                <td>""" + str(i['date_req'].strftime('%d %b %Y')) + f"""</td>
            """
        for d in potential_dates :
            if d in items[i['id']] :
                table_body += f"""<td>""" + str(items[i['id']][d]['quantity']) + f"""</td>
                
            """
            else :
                table_body += f"""<td></td>
            """
        table_body += f"""</tr>"""

    # Generate planned order schedule: ALTERNATE
    items_alt = {}
    for i in selected_items.values().all() :
        # Define the start and end dates
        single_end_date = i['date_req']

        potential_purchase_dates = generate_month_year_dates(start_date, single_end_date)
        remaining_quantity = i['quantity']
        ordered_dates = random.sample(potential_purchase_dates, len(potential_purchase_dates))
        items_alt[i['id']] = {}
        k = 0
        while remaining_quantity > 0 :
            if k < len(ordered_dates) - 1:
                 quantity_purchased = random.randint(1, remaining_quantity)
            else :
                quantity_purchased = remaining_quantity
            items_alt[i['id']][ordered_dates[k]] = {
                'quantity': quantity_purchased
            }
            remaining_quantity -= quantity_purchased
            k += 1
    
    table_body_alt = ''
    for i in selected_items.values().all() :
        table_body_alt += f"""<tr><td>""" + str(i['item_description']) + f"""</td>
                <td class="item-quantity">""" + str(i['quantity']) + f"""</td>
                <td>""" + str(i['criticality']) + f"""</td>
                <td>""" + str(i['date_req'].strftime('%d %b %Y')) + f"""</td>
            """
        for d in potential_dates :
            if d in items_alt[i['id']] :
                table_body_alt += f"""<td>""" + str(items_alt[i['id']][d]['quantity']) + f"""</td>
                
            """
            else :
                table_body_alt += f"""<td></td>
            """
        table_body_alt += f"""</tr>"""

    # Get commodity data
   
    # Replace with your FRED API key
    api_key = os.environ.get("FRED_API_KEY")
    image_urls = []

    for i in selected_items.values().all() :

        # Specify the series ID for plastic pipes
        series_id = commodity_series_mapping[i['item_description']]
        print(i['item_description'])

        # Construct the API URL
        api_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"

        # Make the API request
        response = requests.get(api_url)
        data = response.json()

        # Extract relevant data points
        if "observations" not in data or not data["observations"]:
            continue
        else :
            observations = data["observations"]
            dates = np.asarray([o['date'] for o in observations], dtype='datetime64[s]')
            values = [o['value'] for o in observations]
            values = ['nan' if v == '.' else v for v in values]
            values = np.asarray(values, dtype=float)

            # Create a line chart
            #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
            fig, ax = plt.subplots()
            sns.scatterplot(x = dates, y = values)
            plt.xlabel('Time')
            plt.ylabel('Producer Price Index')
            plt.title(('Producer price index for ' + i['item_description']).title())
            plt.xticks(rotation=45)
            fig.set_tight_layout(True)

            # Save the chart to a buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_urls.append(base64.b64encode(buffer.read()).decode())

    context = {
        "selected_items": selected_items,
        "potential_dates": potential_dates,
        "table_body": table_body,
        "table_body_alt": table_body_alt, 
        "image_urls": image_urls
    }

    return HttpResponse(template.render(context, request))

def industries(request, item_id):
    response = "You're looking at the industries of items %s."
    return HttpResponse(response % item_id)

def edit(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    try :
        print(request.POST["industry"])
        selected_choice = item.supplieritem_set.get(pk=request.POST["industry"].id)
    except (KeyError, SupplierItem.DoesNotExist) :
        return render(
            request, 
            "mainDash/detail.html", 
            {
                "item": item,
                "error_message": "You did not select a supplier."
            }
        )
    return HttpResponse("You're editting question %s." % item_id)

class CSVUploadFormSuppliers(forms.Form):
    csv_file = forms.FileField()

class CSVUploadFormBOM(forms.Form):
    csv_file = forms.FileField()

def upload_supplier_csv(request):
    if request.method == 'POST':
        form = CSVUploadFormSuppliers(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # delete old data first
            Supplier.objects.all().delete()
            Coordenadas.objects.all().delete()

            data = []
            i = 0
            for line in csv_file:
                row = line.decode('utf-8').strip().split(',')
                if i != 0 :
                    new_supplier = Supplier(
                        supplier_name=row[0],
                        naics_code=row[1],
                        location=row[2], 
                        lat = row[3],
                        lon = row[4],
                        quality=row[5],
                        delay_risk=row[6]
                    )

                    new_coord = Coordenadas(
                        supplier = new_supplier,
                        lat = row[3],
                        lon = row[4]
                    )

                    # Save the new instance to the database
                    new_supplier.save()
                    new_coord.save()
                data.append(row)
                i += 1

            return render(request, 'mainDash/uploaded_data.html', {'data': data})
        
    else:
        form = CSVUploadFormSuppliers()
    
    return render(request, 'mainDash/upload_csv.html', {'form': form, 'form_title': 'Upload Supplier Data'})

def upload_bom_csv(request):
    if request.method == 'POST':
        form = CSVUploadFormBOM(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            # delete old data first
            Item.objects.all().delete()

            data = []
            i = 0
            for line in csv_file:
                row = line.decode('utf-8').strip().split(',')
                if i != 0 :
                    new_item = Item(
                        item_description = row[1],
                        date_req = row[5],
                        criticality = row[3],
                        quantity = row[2],
                        naics_code = row[4]
                    )

                    # Save the new instance to the database
                    new_item.save()
                data.append(row)
                i += 1

            return render(request, 'mainDash/uploaded_data.html', {'data': data})
        
    else:
        form = CSVUploadFormBOM()
    
    return render(request, 'mainDash/upload_csv.html', {'form': form, 'form_title': 'Upload BOM Data'})

def generate_month_year_dates(start_date, end_date):
    current_date = start_date
    dates_list = []

    while current_date <= end_date:
        dates_list.append(current_date.strftime('%b %Y'))
        
        # Calculate the last day of the current month
        _, last_day = calendar.monthrange(current_date.year, current_date.month)
        
        # Move to the next month
        current_date = current_date.replace(day=last_day) + timedelta(days=1)
    
    return dates_list