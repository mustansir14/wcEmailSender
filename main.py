from email.message import EmailMessage
import smtplib
from woocommerce import API
from config import *
import json, os
from datetime import datetime, timezone
import pytz
import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

def send_email(to, name):
    msg = EmailMessage()
    msg["From"] = "outreach@graphue.com"
    msg["To"] = to
    msg["Bcc"] = "outreach@graphue.com"
    msg["Subject"] = "Your present from Graphue"
    body_text = """Hi %s, hope you're enjoying your presentation templates!\n\nUp for more good stuff? We've got a present for you.\n\nShow us some love on AppSumo and choose between this awesome Font Bundle or a unique icon or illustration set from our sister website Flat-Icons.com.\n\nAll you have to do is leave a short review on AppSumo (regular or plus) and then tell us what you'd like to get. That's it!\n\nWelcome to the Graphue family 🥂🥳\n\nDarko - Graphue Team\n\nGraphue.com""" % name
    msg.set_content(body_text)
    html = """Hi %s, hope you're enjoying your presentation templates!
<br><br>Up for more good stuff? We've got a present for you.
<br><br>Show us some love on AppSumo and choose between this awesome <a href="https://appsumo.com/products/marketplace-43-fonts-bundle/">Font Bundle</a> or a unique icon or illustration set from our sister website <a href="https://flat-icons.com/">Flat-Icons.com</a>.
<br><br>All you have to do is leave a short review on AppSumo (<a href="https://appsumo.com/products/marketplace-graphue-presentation-templates/">regular</a> or <a href="https://appsumo.com/products/graphue-plus-exclusive/">plus</a>) and then tell us what you'd like to get. That's it!
<br><br>Welcome to the Graphue family 🥂🥳
<br><br>Darko - Graphue Team
<br><br>Graphue.com
""" % name
    msg.add_alternative(html, subtype='html')
    with smtplib.SMTP_SSL(host="smtp.yandex.com", port=465) as smtp_obj:  # ENVIAR DESDE UN DOMINIO PERSONALIZADO.
        smtp_obj.ehlo()
        smtp_obj.login("outreach@graphue.com", "oglqgujfpgpclmrq")
        smtp_obj.send_message(msg)

    logging.info(f"Email sent to {to}")


if __name__ == "__main__":

    wcapi = API(
        url="https://graphue.com/", # Your store URL
        consumer_key=CONSUMER_KEY, # Your consumer key
        consumer_secret=CONSUMER_SECRET, # Your consumer secret
        wp_api=True, # Enable the WP REST API integration
        version="wc/v3" # WooCommerce WP REST API version
    )

    if not os.path.isfile("last_scan_date.txt"):
        last_scan_date = datetime.now(timezone.utc)
    else:
        with open("last_scan_date.txt", "r") as f:
            last_scan_date = datetime.fromisoformat(f.read())

    with open("last_scan_date.txt", "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())
    
    page = 1
    done = False
    while True:
        members = wcapi.get("memberships/members", params={"orderby": "date_created", "per_page": 50, "page": page}).json()
        if len(members) == 0:
            break
        for member in members:
            if datetime.fromisoformat(member["date_created_gmt"]) < last_scan_date:
                done = True
                logging.info("All members done.")
                break

            # get order
            order = wcapi.get(f"orders/{member['order_id']}").json()

            # check if has coupons
            if len(order['coupon_lines']) == 0:
                continue

            # check if coupons have _as or as_
            got_as = False
            for coupon_line in order['coupon_lines']:
                if "_as" in coupon_line['code'] or "as_" in coupon_line['code']:
                    got_as = True
            if not got_as:
                continue
            
            # get customer (to get email)
            customer = wcapi.get(f"customers/{member['customer_id']}").json()
            send_email(customer['email'], customer['first_name'])
            
        if done:
            break
        page += 1

    


