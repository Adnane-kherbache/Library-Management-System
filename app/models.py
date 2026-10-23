from datetime import datetime, timedelta
from app import db


class Book(db.Model):
    """
    Book model representing books in the library
    """
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    publisher = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    available = db.Column(db.Integer, default=1, nullable=False)
    cover_image = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Borrow
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Book {self.title}>'
    
    def is_available(self):
        """Check if book has available copies"""
        return self.available > 0
    
    def borrow_book(self):
        """Decrease available count when book is borrowed"""
        if self.available > 0:
            self.available -= 1
            return True
        return False
    
    def return_book(self):
        """Increase available count when book is returned"""
        if self.available < self.quantity:
            self.available += 1
            return True
        return False
    
    def get_active_borrows(self):
        """Get all active borrows for this book"""
        return self.borrows.filter_by(status='active').all()

    @property
    def total_borrows_count(self):
        """Total times this book was borrowed"""
        return self.borrows.count()
    
    def to_dict(self):
        """Convert book object to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'publication_year': self.publication_year,
            'publisher': self.publisher,
            'description': self.description,
            'quantity': self.quantity,
            'available': self.available,
            'total_borrows': self.total_borrows_count,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Member(db.Model):
    """
    Member model representing library members
    """
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    membership_type = db.Column(db.String(20), default='standard')  # standard, premium
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Borrow
    borrows = db.relationship('Borrow', backref='member', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Member {self.name}>'
    
    def get_active_borrows(self):
        """Get all active borrows for this member"""
        return self.borrows.filter_by(status='active').all()
    
    def get_active_borrows_count(self):
        """Get count of active borrows"""
        return self.borrows.filter_by(status='active').count()

    @property
    def active_borrows_count(self):
        """Property wrapper for active borrows count"""
        return self.get_active_borrows_count()

    @property
    def max_books_allowed(self):
        """Borrow limit based on membership type"""
        return 10 if self.membership_type == 'premium' else 5

    @property
    def standard_loan_days(self):
        """Default loan days based on membership tier"""
        return 30 if self.membership_type == 'premium' else 14
    
    def can_borrow_more(self, max_books=None):
        """Check if member can borrow more books"""
        if max_books is None:
            max_books = self.max_books_allowed
        return self.is_active and (self.get_active_borrows_count() < max_books)
    
    def has_overdue_books(self):
        """Check if member has any overdue books"""
        active_borrows = self.get_active_borrows()
        today = datetime.now()
        for borrow in active_borrows:
            if borrow.due_date < today:
                return True
        return False
    
    def get_total_fines(self):
        """Calculate total outstanding unpaid fines (both unpaid on returned and pending on overdue active)"""
        total_fine = 0.0
        # Fines on returned books that are unpaid
        returned_unpaid = self.borrows.filter(
            Borrow.status == 'returned',
            Borrow.fine_amount > 0,
            Borrow.fine_paid == False
        ).all()
        for b in returned_unpaid:
            total_fine += (b.fine_amount or 0.0)
        
        # Pending fines on currently overdue active books
        active_borrows = self.get_active_borrows()
        for borrow in active_borrows:
            if borrow.is_overdue():
                total_fine += borrow.calculate_fine()
        
        return round(total_fine, 2)
    
    def to_dict(self):
        """Convert member object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'membership_type': self.membership_type,
            'max_books_allowed': self.max_books_allowed,
            'is_active': self.is_active,
            'active_borrows': self.get_active_borrows_count(),
            'has_overdue': self.has_overdue_books(),
            'outstanding_fines': self.get_total_fines()
        }


class Borrow(db.Model):
    """
    Borrow model representing book borrowing transactions
    """
    __tablename__ = 'borrows'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False, index=True)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)  # active, returned, overdue
    notes = db.Column(db.Text, nullable=True)
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Borrow {self.id}: Book {self.book_id} by Member {self.member_id}>'
    
    def is_overdue(self):
        """Check if the borrow is overdue"""
        if self.status == 'returned':
            return False
        return datetime.now() > self.due_date
    
    def days_overdue(self):
        """Calculate number of days overdue"""
        if self.status == 'returned':
            if self.return_date and self.return_date > self.due_date:
                return (self.return_date - self.due_date).days
            return 0
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days
    
    def calculate_fine(self, fine_per_day=1.0):
        """Calculate fine based on overdue days"""
        days = self.days_overdue()
        return round(float(days * fine_per_day), 2)
    
    def return_book(self, fine_paid=False):
        """Mark book as returned and update status"""
        self.return_date = datetime.utcnow()
        self.status = 'returned'
        
        # Calculate fine if overdue
        if self.return_date > self.due_date:
            calculated = self.calculate_fine()
            self.fine_amount = calculated
            self.fine_paid = fine_paid
        else:
            self.fine_amount = 0.0
            self.fine_paid = True
        
        # Update book availability
        if self.book:
            self.book.return_book()
        
        self.updated_at = datetime.utcnow()
        return True
    
    def pay_fine(self):
        """Mark outstanding fine as paid"""
        self.fine_paid = True
        self.updated_at = datetime.utcnow()
        return True

    def waive_fine(self):
        """Waive fine entirely"""
        self.fine_amount = 0.0
        self.fine_paid = True
        self.updated_at = datetime.utcnow()
        return True
    
    def extend_due_date(self, days=7):
        """Extend the due date by specified days"""
        if self.status == 'active' and not self.is_overdue():
            self.due_date += timedelta(days=days)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_status(self):
        """Update status based on current date"""
        if self.status == 'active' and self.is_overdue():
            self.status = 'overdue'
    
    def to_dict(self):
        """Convert borrow object to dictionary"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else None,
            'member_id': self.member_id,
            'member_name': self.member.name if self.member else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'fine_amount': self.fine_amount,
            'fine_paid': self.fine_paid
        }