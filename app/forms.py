from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional


class BookForm(FlaskForm):
    """Form for adding/editing books"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(min=1, max=100, message='Author name must be between 1 and 100 characters')
    ])
    
    isbn = StringField('ISBN', validators=[
        DataRequired(message='ISBN is required'),
        Length(min=10, max=13, message='ISBN must be 10 or 13 characters')
    ])
    
    category = SelectField('Category', choices=[
        ('', 'Select Category'),
        ('Fiction', 'Fiction'),
        ('Non-Fiction', 'Non-Fiction'),
        ('Science Fiction', 'Science Fiction'),
        ('Fantasy', 'Fantasy'),
        ('Mystery', 'Mystery'),
        ('Thriller', 'Thriller'),
        ('Romance', 'Romance'),
        ('Biography', 'Biography'),
        ('History', 'History'),
        ('Science', 'Science'),
        ('Technology', 'Technology'),
        ('Self-Help', 'Self-Help'),
        ('Children', 'Children'),
        ('Young Adult', 'Young Adult'),
        ('Poetry', 'Poetry'),
        ('Drama', 'Drama'),
        ('Other', 'Other')
    ], validators=[Optional()])
    
    publication_year = IntegerField('Publication Year', validators=[
        Optional(),
        NumberRange(min=1000, max=2100, message='Please enter a valid year')
    ])
    
    publisher = StringField('Publisher', validators=[
        Optional(),
        Length(max=100, message='Publisher name must not exceed 100 characters')
    ])
    
    description = TextAreaField('Description', validators=[Optional()])
    
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, message='Quantity must be at least 1')
    ])


class MemberForm(FlaskForm):
    """Form for adding/editing members"""
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email must not exceed 120 characters')
    ])
    
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message='Phone number must not exceed 20 characters')
    ])
    
    address = TextAreaField('Address', validators=[Optional()])
    
    membership_type = SelectField('Membership Type', choices=[
        ('standard', 'Standard'),
        ('premium', 'Premium')
    ], validators=[DataRequired()])
    
    is_active = BooleanField('Active Member', default=True)


class BorrowForm(FlaskForm):
    """Form for checkout"""
    book_id = SelectField('Book', coerce=int, validators=[
        DataRequired(message='Please select a book')
    ])
    
    member_id = SelectField('Member', coerce=int, validators=[
        DataRequired(message='Please select a member')
    ])
    
    borrow_days = SelectField('Borrowing Period', choices=[
        (7, '7 Days (1 Week)'),
        (14, '14 Days (2 Weeks)'),
        (21, '21 Days (3 Weeks)'),
        (30, '30 Days (1 Month)')
    ], coerce=int, default=14, validators=[DataRequired()])


class SearchForm(FlaskForm):
    """Form for search"""
    query = StringField('Search', validators=[
        DataRequired(message='Please enter a search query'),
        Length(min=1, max=100)
    ])