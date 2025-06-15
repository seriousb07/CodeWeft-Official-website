from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, constr
from dotenv import load_dotenv
import os
import re
import emails

app = FastAPI()

# Load environment variables
load_dotenv()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Email configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")  # Set in .env file
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # Set in .env file

# Pydantic model for contact form
class ContactForm(BaseModel):
    name: constr(min_length=1, max_length=100)
    number: constr(min_length=10, max_length=15)
    msg: constr(min_length=1, max_length=1000)
    product: constr(min_length=1)
    email: EmailStr

# Pydantic model for newsletter form
class NewsletterForm(BaseModel):
    email: EmailStr

# Validate phone number
def validate_phone_number(number: str) -> bool:
    phone_regex = re.compile(r"^\+?\d{10,15}$")
    return bool(phone_regex.match(number))

# Send email utility
async def send_email(to_email: str, subject: str, body: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        raise HTTPException(status_code=500, detail="SMTP credentials not configured")
    
    message = emails.Message(
        text=body,
        subject=subject,
        mail_from=SMTP_USER,
        mail_to=to_email
    )

    try:
        smtp_options = {
            "host": SMTP_HOST,
            "port": SMTP_PORT,
            "user": SMTP_USER,
            "password": SMTP_PASSWORD,
            "tls": True
        }
        response = message.send(smtp=smtp_options)
        if response.status_code not in (250,):
            raise HTTPException(status_code=500, detail=f"Failed to send email: {response.status_text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Serve the homepage
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Serve products page (optional, if products.html exists)
@app.get("/products", response_class=HTMLResponse)
async def get_products(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

# Serve demo page (optional, if demo.html exists)
@app.get("/demo", response_class=HTMLResponse)
async def get_demo(request: Request):
    return templates.TemplateResponse("demo.html", {"request": request})

# Handle contact form submission
@app.post("/contact")
async def submit_contact(
    name: str = Form(...),
    number: str = Form(...),
    msg: str = Form(...),
    product: str = Form(...),
    email: str = Form(...)
):
    # Validate form data
    try:
        form_data = ContactForm(name=name, number=number, msg=msg, product=product, email=email)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not validate_phone_number(number):
        raise HTTPException(status_code=422, detail="Invalid phone number (10-15 digits, optional country code).")

    # Prepare email content
    body = f"""
    New Contact Form Submission:
    Name: {name}
    Email: {email}
    Phone Number: {number}
    Product: {product}
    Message: {msg}
    """
    
    # Send email to your address
    await send_email(
        to_email="shreyashbhagwat505@gmail.com",
        subject="New Contact Form Submission",
        body=body
    )

    return {"message": "Message sent successfully"}

# Handle newsletter form submission
@app.post("/newsletter")
async def submit_newsletter(email: str = Form(...)):
    # Validate email
    try:
        form_data = NewsletterForm(email=email)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Prepare email content
    body = f"""
    New Newsletter Subscription:
    Email: {email}
    """

    # Send email to your address
    await send_email(
        to_email="shreyashbhagwat505@gmail.com",
        subject="New Newsletter Subscription",
        body=body
    )

    return {"message": "Subscribed successfully"}