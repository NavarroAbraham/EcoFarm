from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from decimal import Decimal
import uuid
import os
import re
from datetime import datetime

app = Flask(__name__)
app.url_map.strict_slashes = False

# Database configuration - using the same SQLite database
db_url = os.getenv('FLASK_DATABASE_URL') or os.getenv('DATABASE_URL') or 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Models (copied from Django models)
class Product(db.Model):
    __tablename__ = 'core_product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100), default='Organic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'core_order'
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    product_id = db.Column(db.Integer, db.ForeignKey('core_product.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mark_paid(self):
        self.status = self.STATUS_PAID
        db.session.commit()

    def mark_failed(self):
        self.status = self.STATUS_FAILED
        db.session.commit()

class Payment(db.Model):
    __tablename__ = 'core_payment'
    STATUS_PENDING = 'pending'
    STATUS_SUCCEEDED = 'succeeded'
    STATUS_FAILED = 'failed'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('core_order.id'), nullable=False)
    provider = db.Column(db.String(40), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    external_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mark_succeeded(self, external_id):
        self.status = self.STATUS_SUCCEEDED
        self.external_id = external_id
        db.session.commit()

    def mark_failed(self):
        self.status = self.STATUS_FAILED
        db.session.commit()

class Certificate(db.Model):
    __tablename__ = 'core_certificate'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    pdf_data = db.Column(db.LargeBinary)  # Store PDF binary data

    def generate_certificate_number(self):
        """Generate a unique certificate number"""
        import random
        import string
        while True:
            number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not Certificate.query.filter_by(certificate_number=number).first():
                self.certificate_number = f"CERT-{number}"
                break

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Schemas
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order

class PaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Payment

class CertificateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificate

order_schema = OrderSchema()
payment_schema = PaymentSchema()
certificate_schema = CertificateSchema()

# Business logic
class OrderBuilder:
    def build(self, data):
        order = Order(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            total_amount=Decimal(str(data['total_amount'])),
        )
        # Basic validation
        if order.total_amount <= 0:
            raise ValueError("Total amount must be greater than zero")
        db.session.add(order)
        db.session.commit()
        return order

class PaymentProcessor:
    def charge(self, order, provider):
        raise NotImplementedError

class DummyPaymentProcessor(PaymentProcessor):
    def charge(self, order, provider):
        payment = Payment(
            order_id=order.id,
            provider=provider,
            amount=order.total_amount,
            status=Payment.STATUS_PENDING,
        )
        db.session.add(payment)
        db.session.commit()
        payment.mark_succeeded(str(uuid.uuid4()))
        order.mark_paid()
        return payment

class PaymentProcessorFactory:
    def get_processor(self, provider):
        if provider == 'dummy':
            return DummyPaymentProcessor()
        raise ValueError(f"Unsupported provider: {provider}")

class OrderPaymentService:
    def __init__(self, builder=None, factory=None):
        self.builder = builder or OrderBuilder()
        self.factory = factory or PaymentProcessorFactory()

    def create_order_and_payment(self, data):
        order = self.builder.build(data)
        processor = self.factory.get_processor(data['provider'])
        payment = processor.charge(order, data['provider'])
        return order, payment

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from reportlab.lib.colors import blue, black
from io import BytesIO

class CertificateGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_certificate_pdf(self, certificate):
        """Generate PDF certificate and return binary data"""
        buffer = BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Title style
        title_style = ParagraphStyle(
            'CertificateTitle',
            parent=self.styles['Heading1'],
            fontSize=36,
            textColor=blue,
            alignment=1,  # Center alignment
            spaceAfter=30
        )

        # Certificate title
        elements.append(Paragraph("CERTIFICATE OF COMPLETION", title_style))
        elements.append(Spacer(1, 0.5*inch))

        # Main text style
        main_style = ParagraphStyle(
            'MainText',
            parent=self.styles['Normal'],
            fontSize=16,
            alignment=1,
            spaceAfter=20
        )

        # Certificate content
        elements.append(Paragraph("This is to certify that", main_style))
        elements.append(Spacer(1, 0.2*inch))

        # Student name (larger, bold)
        name_style = ParagraphStyle(
            'NameStyle',
            parent=self.styles['Normal'],
            fontSize=24,
            textColor=blue,
            alignment=1,
            spaceAfter=20
        )
        elements.append(Paragraph(certificate.customer_name, name_style))
        elements.append(Spacer(1, 0.2*inch))

        # Course completion text
        elements.append(Paragraph("has successfully completed the course", main_style))
        elements.append(Spacer(1, 0.2*inch))

        # Course name
        course_style = ParagraphStyle(
            'CourseStyle',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=black,
            alignment=1,
            spaceAfter=30
        )
        elements.append(Paragraph(f'"{certificate.course_name}"', course_style))
        elements.append(Spacer(1, 0.5*inch))

        # Date and certificate number
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=1,
            spaceAfter=10
        )

        issued_date = certificate.issued_date.strftime("%B %d, %Y")
        elements.append(Paragraph(f"Issued on: {issued_date}", date_style))
        elements.append(Paragraph(f"Certificate Number: {certificate.certificate_number}", date_style))

        # Build the PDF
        doc.build(elements)

        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

class CertificateService:
    def __init__(self, generator=None):
        self.generator = generator or CertificateGenerator()

    def create_certificate(self, data):
        """Create a certificate and generate PDF"""
        certificate = Certificate(
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            course_name=data['course_name']
        )

        # Generate unique certificate number
        certificate.generate_certificate_number()

        # Generate PDF
        pdf_data = self.generator.generate_certificate_pdf(certificate)
        certificate.pdf_data = pdf_data

        # Save to database
        db.session.add(certificate)
        db.session.commit()

        return certificate

# API Routes
@app.route('/api/v2/orders/', methods=['GET'])
def list_orders():
    try:
        orders = Order.query.all()
        return jsonify({'orders': order_schema.dump(orders, many=True)}), 200
    except Exception as e:
        app.logger.error(f"Error retrieving orders: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/v2/orders/', methods=['POST'])
def create_order_payment():
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'total_amount', 'provider']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'code': 'MISSING_FIELD'
                }), 400

        # Validate data types
        try:
            data['total_amount'] = float(data['total_amount'])
        except (ValueError, TypeError):
            return jsonify({
                'error': 'total_amount must be a valid number',
                'code': 'INVALID_AMOUNT'
            }), 400

        if data['total_amount'] <= 0:
            return jsonify({
                'error': 'total_amount must be greater than zero',
                'code': 'INVALID_AMOUNT'
            }), 400

        # Create order and payment
        service = OrderPaymentService()
        order, payment = service.create_order_and_payment(data)

        return jsonify({
            'order': order_schema.dump(order),
            'payment': payment_schema.dump(payment)
        }), 201

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        with open('error.log', 'a') as f:
            f.write(f"ERROR: {error_msg}\n---\n")
        print(f"ERROR: {error_msg}", flush=True)
        app.logger.error(f"Unexpected error: {error_msg}")
        return jsonify({
            'error': str(e),
            'traceback': error_msg,
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/v2/orders/<int:order_id>/', methods=['GET'])
def get_order(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify(order_schema.dump(order)), 200
    except Exception as e:
        app.logger.error(f"Error retrieving order {order_id}: {str(e)}")
        return jsonify({
            'error': 'Order not found',
            'code': 'NOT_FOUND'
        }), 404

@app.route('/', methods=['GET'])
@app.route('/api/v2/', methods=['GET'])
@app.route('/api/v2/health/', methods=['GET'])
@app.route('/health/', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'flask_service',
        'endpoints': [
            '/health/',
            '/api/v2/',
            '/api/v2/orders/',
            '/api/v2/certificates/'
        ]
    }), 200

# Certificate API Routes
@app.route('/api/v2/certificates/', methods=['POST'])
def create_certificate():
    """Create a new certificate and generate PDF"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['customer_name', 'customer_email', 'course_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}',
                    'code': 'MISSING_FIELD'
                }), 400

        # Validate email format (basic validation)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['customer_email']):
            return jsonify({
                'error': 'Invalid email format',
                'code': 'INVALID_EMAIL'
            }), 400

        # Create certificate
        service = CertificateService()
        certificate = service.create_certificate(data)

        return jsonify({
            'certificate': certificate_schema.dump(certificate),
            'download_url': f'/api/v2/certificates/{certificate.id}/download/'
        }), 201

    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        app.logger.error(f"Unexpected error creating certificate: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR'
        }), 500

@app.route('/api/v2/certificates/<int:certificate_id>/', methods=['GET'])
def get_certificate(certificate_id):
    """Get certificate details"""
    try:
        certificate = Certificate.query.get_or_404(certificate_id)
        return jsonify(certificate_schema.dump(certificate)), 200
    except Exception as e:
        app.logger.error(f"Error retrieving certificate {certificate_id}: {str(e)}")
        return jsonify({
            'error': 'Certificate not found',
            'code': 'NOT_FOUND'
        }), 404

from flask import send_file

@app.route('/api/v2/certificates/<int:certificate_id>/download/', methods=['GET'])
def download_certificate(certificate_id):
    """Download certificate PDF"""
    try:
        certificate = Certificate.query.get_or_404(certificate_id)

        if not certificate.pdf_data:
            return jsonify({
                'error': 'Certificate PDF not available',
                'code': 'PDF_NOT_FOUND'
            }), 404

        # Create a BytesIO object from the PDF data
        pdf_buffer = BytesIO(certificate.pdf_data)

        # Generate filename
        filename = f"certificate_{certificate.certificate_number}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        app.logger.error(f"Error downloading certificate {certificate_id}: {str(e)}")
        return jsonify({
            'error': 'Error downloading certificate',
            'code': 'DOWNLOAD_ERROR'
        }), 500

if __name__ == '__main__':
    debug_enabled = os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes', 'on')
    app.run(host='0.0.0.0', port=5000, debug=debug_enabled)
