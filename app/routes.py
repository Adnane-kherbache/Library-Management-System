from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from sqlalchemy import or_, func, case
from app import db
from app.models import Book, Member, Borrow

# Create Blueprint
main_bp = Blueprint('main', __name__)


# ==================== HOME & DASHBOARD ====================

@main_bp.route('/')
def index():
    """Home page with dashboard statistics and activity metrics"""
    today = datetime.now()
    
    # Core counts
    total_books = Book.query.count()
    total_copies = db.session.query(func.coalesce(func.sum(Book.quantity), 0)).scalar()
    available_copies = db.session.query(func.coalesce(func.sum(Book.available), 0)).scalar()
    total_members = Member.query.count()
    active_borrows_count = Borrow.query.filter_by(status='active').count()
    
    # Overdue borrows
    overdue_borrows = Borrow.query.filter(
        Borrow.status == 'active',
        Borrow.due_date < today
    ).order_by(Borrow.due_date.asc()).all()
    overdue_count = len(overdue_borrows)
    
    # Fines metrics
    paid_fines_sum = db.session.query(
        func.coalesce(func.sum(Borrow.fine_amount), 0.0)
    ).filter(Borrow.fine_paid == True).scalar()
    
    unpaid_returned_fines_sum = db.session.query(
        func.coalesce(func.sum(Borrow.fine_amount), 0.0)
    ).filter(Borrow.status == 'returned', Borrow.fine_paid == False).scalar()
    
    pending_overdue_fines = sum(b.calculate_fine() for b in overdue_borrows)
    total_unpaid_fines = round(unpaid_returned_fines_sum + pending_overdue_fines, 2)
    
    # Recently added books
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(6).all()
    
    # Most borrowed books
    most_borrowed = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        Book.category,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow, Book.id == Borrow.book_id)\
     .group_by(Book.id)\
     .order_by(func.count(Borrow.id).desc())\
     .limit(5).all()
    
    # Recent borrow activities
    recent_activities = Borrow.query.order_by(Borrow.created_at.desc()).limit(6).all()
    
    return render_template(
        'index.html',
        total_books=total_books,
        total_copies=total_copies,
        available_copies=available_copies,
        total_members=total_members,
        active_borrows=active_borrows_count,
        overdue_count=overdue_count,
        paid_fines=round(paid_fines_sum, 2),
        unpaid_fines=total_unpaid_fines,
        recent_books=recent_books,
        most_borrowed=most_borrowed,
        overdue_borrows=overdue_borrows[:5],
        recent_activities=recent_activities
    )


# ==================== BOOKS ROUTES ====================

@main_bp.route('/books')
def books_list():
    """List all books with search, category filtering, and sorting"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    availability = request.args.get('availability', '').strip()
    sort_by = request.args.get('sort', 'title_asc')
    view_mode = request.args.get('view', 'grid')  # grid or table
    per_page = 12 if view_mode == 'grid' else 10
    
    query = Book.query
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%'),
                Book.publisher.ilike(f'%{search}%')
            )
        )
    
    # Category filter
    if category:
        query = query.filter_by(category=category)
        
    # Availability filter
    if availability == 'available':
        query = query.filter(Book.available > 0)
    elif availability == 'borrowed':
        query = query.filter(Book.available == 0)
    
    # Sorting
    if sort_by == 'title_asc':
        query = query.order_by(Book.title.asc())
    elif sort_by == 'title_desc':
        query = query.order_by(Book.title.desc())
    elif sort_by == 'author':
        query = query.order_by(Book.author.asc())
    elif sort_by == 'newest':
        query = query.order_by(Book.created_at.desc())
    elif sort_by == 'popular':
        query = query.outerjoin(Borrow).group_by(Book.id).order_by(func.count(Borrow.id).desc())
    else:
        query = query.order_by(Book.title.asc())
    
    # Pagination
    books = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Distinct categories for filter
    categories = db.session.query(Book.category).filter(Book.category.isnot(None), Book.category != '').distinct().all()
    categories = sorted([c[0] for c in categories if c[0]])
    
    return render_template(
        'books/list.html',
        books=books,
        search=search,
        category=category,
        availability=availability,
        sort_by=sort_by,
        view_mode=view_mode,
        categories=categories
    )


@main_bp.route('/books/add', methods=['GET', 'POST'])
def books_add():
    """Add a new book to the catalog"""
    if request.method == 'POST':
        try:
            isbn = request.form.get('isbn', '').strip()
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            quantity = request.form.get('quantity', type=int, default=1)
            
            # Validation
            if not title or not author or not isbn:
                flash('Title, Author, and ISBN are mandatory fields.', 'danger')
                return render_template('books/add.html')
            
            # Check duplicate ISBN
            existing = Book.query.filter_by(isbn=isbn).first()
            if existing:
                flash(f'A book with ISBN "{isbn}" already exists ({existing.title}).', 'warning')
                return render_template('books/add.html')
            
            if quantity < 1:
                quantity = 1
            
            book = Book(
                title=title,
                author=author,
                isbn=isbn,
                category=request.form.get('category', '').strip() or None,
                publication_year=request.form.get('publication_year', type=int),
                publisher=request.form.get('publisher', '').strip() or None,
                description=request.form.get('description', '').strip() or None,
                quantity=quantity,
                available=quantity
            )
            
            db.session.add(book)
            db.session.commit()
            
            flash(f'Book "{book.title}" added to catalog successfully!', 'success')
            return redirect(url_for('main.books_detail', id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding book: {str(e)}', 'danger')
    
    return render_template('books/add.html')


@main_bp.route('/books/<int:id>')
def books_detail(id):
    """View book details, availability, and borrowing history"""
    book = Book.query.get_or_404(id)
    
    # Active borrows
    active_borrows = book.get_active_borrows()
    
    # Borrow history
    borrow_history = Borrow.query.filter_by(book_id=id).order_by(
        Borrow.borrow_date.desc()
    ).limit(15).all()
    
    total_borrows = Borrow.query.filter_by(book_id=id).count()
    
    return render_template(
        'books/detail.html',
        book=book,
        active_borrows=active_borrows,
        borrow_history=borrow_history,
        total_borrows=total_borrows
    )


@main_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
def books_edit(id):
    """Edit book information and manage stock"""
    book = Book.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            isbn = request.form.get('isbn', '').strip()
            
            # Check if ISBN changed and already exists elsewhere
            if isbn != book.isbn:
                existing = Book.query.filter_by(isbn=isbn).first()
                if existing and existing.id != book.id:
                    flash(f'Another book already has ISBN "{isbn}".', 'danger')
                    return render_template('books/edit.html', book=book)
            
            book.title = request.form.get('title', '').strip()
            book.author = request.form.get('author', '').strip()
            book.isbn = isbn
            book.category = request.form.get('category', '').strip() or None
            book.publication_year = request.form.get('publication_year', type=int)
            book.publisher = request.form.get('publisher', '').strip() or None
            book.description = request.form.get('description', '').strip() or None
            
            # Update quantity safely
            new_quantity = request.form.get('quantity', type=int, default=book.quantity)
            if new_quantity < 1:
                new_quantity = 1
                
            currently_borrowed = book.quantity - book.available
            if new_quantity < currently_borrowed:
                flash(
                    f'Cannot reduce total copies to {new_quantity}. '
                    f'There are currently {currently_borrowed} copies checked out!',
                    'danger'
                )
                return render_template('books/edit.html', book=book)
            
            book.quantity = new_quantity
            book.available = new_quantity - currently_borrowed
            book.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Book information updated successfully!', 'success')
            return redirect(url_for('main.books_detail', id=book.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating book: {str(e)}', 'danger')
    
    return render_template('books/edit.html', book=book)


@main_bp.route('/books/<int:id>/delete', methods=['POST'])
def books_delete(id):
    """Delete a book from catalog"""
    book = Book.query.get_or_404(id)
    
    # Check if book has active borrows
    active_borrows = book.get_active_borrows()
    if active_borrows:
        flash(f'Cannot delete "{book.title}". There are {len(active_borrows)} copies currently checked out!', 'danger')
        return redirect(url_for('main.books_detail', id=id))
    
    try:
        title = book.title
        db.session.delete(book)
        db.session.commit()
        flash(f'Book "{title}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')
    
    return redirect(url_for('main.books_list'))


# ==================== MEMBERS ROUTES ====================

@main_bp.route('/members')
def members_list():
    """List library members with search and filter options"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    tier = request.args.get('tier', '').strip()
    status = request.args.get('status', '').strip()
    per_page = 10
    
    query = Member.query
    
    # Search filter
    if search:
        query = query.filter(
            or_(
                Member.name.ilike(f'%{search}%'),
                Member.email.ilike(f'%{search}%'),
                Member.phone.ilike(f'%{search}%')
            )
        )
    
    # Tier filter
    if tier:
        query = query.filter_by(membership_type=tier)
        
    # Status filter
    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)
    
    members = query.order_by(Member.name.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'members/list.html',
        members=members,
        search=search,
        tier=tier,
        status=status
    )


@main_bp.route('/members/add', methods=['GET', 'POST'])
def members_add():
    """Register a new library member"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            membership_type = request.form.get('membership_type', 'standard')
            
            if not name or not email:
                flash('Name and Email are required fields.', 'danger')
                return render_template('members/add.html')
            
            # Check existing email
            if Member.query.filter_by(email=email).first():
                flash(f'A member with email "{email}" is already registered.', 'warning')
                return render_template('members/add.html')
            
            member = Member(
                name=name,
                email=email,
                phone=phone or None,
                address=address or None,
                membership_type=membership_type,
                is_active=True
            )
            
            db.session.add(member)
            db.session.commit()
            
            flash(f'Member "{member.name}" successfully registered!', 'success')
            return redirect(url_for('main.members_detail', id=member.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding member: {str(e)}', 'danger')
    
    return render_template('members/add.html')


@main_bp.route('/members/<int:id>')
def members_detail(id):
    """View member profile, borrowing capacity, active loans, and fines"""
    member = Member.query.get_or_404(id)
    
    active_borrows = member.get_active_borrows()
    borrow_history = Borrow.query.filter_by(member_id=id).order_by(
        Borrow.borrow_date.desc()
    ).all()
    
    total_fines = member.get_total_fines()
    
    return render_template(
        'members/detail.html',
        member=member,
        active_borrows=active_borrows,
        borrow_history=borrow_history,
        total_fines=total_fines
    )


@main_bp.route('/members/<int:id>/edit', methods=['GET', 'POST'])
def members_edit(id):
    """Edit member profile and membership settings"""
    member = Member.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            
            # Check unique email
            if email != member.email:
                existing = Member.query.filter_by(email=email).first()
                if existing and existing.id != member.id:
                    flash(f'Email "{email}" is already taken by another member.', 'danger')
                    return render_template('members/edit.html', member=member)
            
            member.name = request.form.get('name', '').strip()
            member.email = email
            member.phone = request.form.get('phone', '').strip() or None
            member.address = request.form.get('address', '').strip() or None
            member.membership_type = request.form.get('membership_type', 'standard')
            member.is_active = (request.form.get('is_active') == 'on')
            member.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Member profile updated successfully!', 'success')
            return redirect(url_for('main.members_detail', id=member.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating member: {str(e)}', 'danger')
    
    return render_template('members/edit.html', member=member)


@main_bp.route('/members/<int:id>/delete', methods=['POST'])
def members_delete(id):
    """Delete a library member"""
    member = Member.query.get_or_404(id)
    
    active_borrows = member.get_active_borrows()
    if active_borrows:
        flash(f'Cannot delete member "{member.name}" because they have {len(active_borrows)} unreturned books!', 'danger')
        return redirect(url_for('main.members_detail', id=id))
    
    try:
        name = member.name
        db.session.delete(member)
        db.session.commit()
        flash(f'Member "{name}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting member: {str(e)}', 'danger')
    
    return redirect(url_for('main.members_list'))


# ==================== BORROWS & LOANS ROUTES ====================

@main_bp.route('/borrows')
def borrows_list():
    """List borrowing transactions with status and search filters"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()
    per_page = 15
    today = datetime.now()
    
    query = Borrow.query.join(Book).join(Member)
    
    # Status filter
    if status == 'active':
        query = query.filter(Borrow.status == 'active', Borrow.due_date >= today)
    elif status == 'overdue':
        query = query.filter(Borrow.status == 'active', Borrow.due_date < today)
    elif status == 'returned':
        query = query.filter(Borrow.status == 'returned')
    
    # Search
    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f'%{search}%'),
                Member.name.ilike(f'%{search}%'),
                Member.email.ilike(f'%{search}%')
            )
        )
    
    borrows = query.order_by(Borrow.borrow_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template(
        'borrows/list.html',
        borrows=borrows,
        status=status,
        search=search
    )


@main_bp.route('/borrows/checkout', methods=['GET', 'POST'])
def borrows_checkout():
    """Checkout a book to a member"""
    preset_book_id = request.args.get('book_id', type=int)
    preset_member_id = request.args.get('member_id', type=int)
    
    if request.method == 'POST':
        try:
            book_id = request.form.get('book_id', type=int)
            member_id = request.form.get('member_id', type=int)
            borrow_days = request.form.get('borrow_days', type=int)
            notes = request.form.get('notes', '').strip() or None
            
            book = Book.query.get_or_404(book_id)
            member = Member.query.get_or_404(member_id)
            
            # Validation
            if not book.is_available():
                flash(f'"{book.title}" is currently out of stock!', 'danger')
                return redirect(url_for('main.borrows_checkout'))
            
            if not member.is_active:
                flash(f'Member "{member.name}" is currently marked inactive and cannot borrow books.', 'danger')
                return redirect(url_for('main.borrows_checkout'))
            
            if not member.can_borrow_more():
                flash(
                    f'Member "{member.name}" has reached their borrowing limit '
                    f'({member.max_books_allowed} books max for {member.membership_type} tier).',
                    'danger'
                )
                return redirect(url_for('main.borrows_checkout'))
            
            if member.has_overdue_books():
                flash(f'Note: Member "{member.name}" currently has overdue books on file.', 'warning')
            
            if not borrow_days or borrow_days < 1:
                borrow_days = member.standard_loan_days
            
            # Create borrow record
            borrow = Borrow(
                book_id=book_id,
                member_id=member_id,
                borrow_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=borrow_days),
                status='active',
                notes=notes
            )
            
            # Update book inventory
            book.borrow_book()
            
            db.session.add(borrow)
            db.session.commit()
            
            flash(
                f'Book "{book.title}" checked out to {member.name}! '
                f'Due date: {borrow.due_date.strftime("%b %d, %Y")}',
                'success'
            )
            return redirect(url_for('main.borrows_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error checking out book: {str(e)}', 'danger')
    
    # Available books & active members
    books = Book.query.filter(Book.available > 0).order_by(Book.title.asc()).all()
    members = Member.query.filter_by(is_active=True).order_by(Member.name.asc()).all()
    
    return render_template(
        'borrows/checkout.html',
        books=books,
        members=members,
        preset_book_id=preset_book_id,
        preset_member_id=preset_member_id
    )


@main_bp.route('/borrows/<int:id>/return', methods=['GET', 'POST'])
def borrows_return(id):
    """Process return of a borrowed book with optional fine settlement"""
    borrow = Borrow.query.get_or_404(id)
    
    if borrow.status != 'active':
        flash('This borrowing record has already been marked returned!', 'warning')
        return redirect(url_for('main.borrows_list'))
    
    overdue_days = borrow.days_overdue()
    fine_amount = borrow.calculate_fine() if borrow.is_overdue() else 0.0

    if request.method == 'POST':
        try:
            pay_now = request.form.get('pay_fine') == 'on' or request.args.get('pay_fine') == '1'
            borrow.return_book(fine_paid=pay_now)
            db.session.commit()
            
            if fine_amount > 0:
                if pay_now:
                    flash(f'Book returned! Late fine of ${fine_amount:.2f} ({overdue_days} days late) was marked as PAID.', 'success')
                else:
                    flash(f'Book returned! Late fine of ${fine_amount:.2f} ({overdue_days} days late) recorded as UNPAID on member account.', 'warning')
            else:
                flash(f'"{borrow.book.title}" returned successfully on time!', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing return: {str(e)}', 'danger')
        
        return redirect(url_for('main.borrows_list'))
    
    return render_template(
        'borrows/return.html',
        borrow=borrow,
        overdue_days=overdue_days,
        fine_amount=fine_amount
    )


@main_bp.route('/borrows/<int:id>/extend', methods=['POST'])
def borrows_extend(id):
    """Extend borrow due date by 7 or 14 days"""
    borrow = Borrow.query.get_or_404(id)
    days = request.form.get('days', 7, type=int)
    
    if borrow.extend_due_date(days=days):
        db.session.commit()
        flash(f'Due date extended by {days} days! New due date: {borrow.due_date.strftime("%b %d, %Y")}', 'success')
    else:
        flash('Cannot extend overdue books or books already returned!', 'danger')
    
    next_url = request.referrer or url_for('main.borrows_list')
    return redirect(next_url)


# ==================== FINES MANAGEMENT (CORE FEATURE) ====================

@main_bp.route('/fines')
def fines_list():
    """Dedicated Fines and Fee Management Dashboard"""
    filter_status = request.args.get('status', 'all')  # all, unpaid, paid
    today = datetime.now()
    
    # Query all borrows that have or had fines
    # 1. Returned borrows with fine_amount > 0
    # 2. Active borrows that are overdue
    returned_with_fines = Borrow.query.filter(
        Borrow.status == 'returned',
        Borrow.fine_amount > 0
    ).all()
    
    active_overdue = Borrow.query.filter(
        Borrow.status == 'active',
        Borrow.due_date < today
    ).all()
    
    # Metrics
    total_paid_fines = sum(b.fine_amount for b in returned_with_fines if b.fine_paid)
    unpaid_returned_fines = sum(b.fine_amount for b in returned_with_fines if not b.fine_paid)
    pending_active_fines = sum(b.calculate_fine() for b in active_overdue)
    total_unpaid_fines = unpaid_returned_fines + pending_active_fines
    total_fines_accrued = total_paid_fines + total_unpaid_fines
    
    # Build list of fine records for display
    fine_records = []
    
    # Add active overdue borrows
    for b in active_overdue:
        fine_records.append({
            'borrow': b,
            'type': 'active_overdue',
            'days_overdue': b.days_overdue(),
            'amount': b.calculate_fine(),
            'is_paid': False,
            'status_label': 'Pending (Active Overdue)'
        })
    
    # Add returned borrows with fines
    for b in returned_with_fines:
        fine_records.append({
            'borrow': b,
            'type': 'returned',
            'days_overdue': b.days_overdue(),
            'amount': b.fine_amount,
            'is_paid': b.fine_paid,
            'status_label': 'Paid' if b.fine_paid else 'Unpaid (Returned)'
        })
    
    # Apply filter
    if filter_status == 'unpaid':
        fine_records = [f for f in fine_records if not f['is_paid']]
    elif filter_status == 'paid':
        fine_records = [f for f in fine_records if f['is_paid']]
    
    # Sort by days overdue descending
    fine_records.sort(key=lambda x: x['days_overdue'], reverse=True)
    
    return render_template(
        'fines/list.html',
        fine_records=fine_records,
        filter_status=filter_status,
        total_paid_fines=round(total_paid_fines, 2),
        total_unpaid_fines=round(total_unpaid_fines, 2),
        total_fines_accrued=round(total_fines_accrued, 2),
        overdue_count=len(active_overdue)
    )


@main_bp.route('/borrows/<int:id>/pay-fine', methods=['POST'])
def borrows_pay_fine(id):
    """Mark fine as paid"""
    borrow = Borrow.query.get_or_404(id)
    
    # If active and overdue, returning is also an option, or paying pending fine
    if borrow.status == 'active' and borrow.is_overdue():
        # Set accrued fine
        borrow.fine_amount = borrow.calculate_fine()
        borrow.fine_paid = True
    else:
        borrow.pay_fine()
        
    db.session.commit()
    flash(f'Fine of ${borrow.fine_amount:.2f} for "{borrow.book.title}" was marked as PAID.', 'success')
    return redirect(request.referrer or url_for('main.fines_list'))


@main_bp.route('/borrows/<int:id>/waive-fine', methods=['POST'])
def borrows_waive_fine(id):
    """Waive/forgive fine"""
    borrow = Borrow.query.get_or_404(id)
    borrow.waive_fine()
    db.session.commit()
    flash(f'Fine for "{borrow.book.title}" was successfully waived.', 'info')
    return redirect(request.referrer or url_for('main.fines_list'))


# ==================== STATISTICS & ANALYTICS (CORE FEATURE) ====================

@main_bp.route('/analytics')
def analytics_view():
    """Dedicated Analytics and Visual Insights Hub"""
    today = datetime.now()
    
    # General metrics
    total_books = Book.query.count()
    total_members = Member.query.count()
    active_borrows = Borrow.query.filter_by(status='active').count()
    returned_borrows = Borrow.query.filter_by(status='returned').count()
    overdue_borrows = Borrow.query.filter(Borrow.status == 'active', Borrow.due_date < today).count()
    
    # Category distribution
    category_counts = db.session.query(
        Book.category,
        func.count(Book.id)
    ).group_by(Book.category).all()
    
    category_labels = [c[0] or 'Uncategorized' for c in category_counts]
    category_data = [c[1] for c in category_counts]
    
    # Membership type breakdown
    standard_members = Member.query.filter_by(membership_type='standard').count()
    premium_members = Member.query.filter_by(membership_type='premium').count()
    
    # Fines metrics
    paid_fines = db.session.query(
        func.coalesce(func.sum(Borrow.fine_amount), 0.0)
    ).filter(Borrow.fine_paid == True).scalar()
    
    unpaid_fines = db.session.query(
        func.coalesce(func.sum(Borrow.fine_amount), 0.0)
    ).filter(Borrow.status == 'returned', Borrow.fine_paid == False).scalar()
    
    # Top 5 most active members
    top_members = db.session.query(
        Member.id,
        Member.name,
        Member.email,
        Member.membership_type,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow, Member.id == Borrow.member_id)\
     .group_by(Member.id)\
     .order_by(func.count(Borrow.id).desc())\
     .limit(5).all()
    
    # Top 5 most borrowed books
    top_books = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        Book.category,
        func.count(Borrow.id).label('borrow_count')
    ).join(Borrow, Book.id == Borrow.book_id)\
     .group_by(Book.id)\
     .order_by(func.count(Borrow.id).desc())\
     .limit(5).all()
    
    return render_template(
        'analytics/index.html',
        total_books=total_books,
        total_members=total_members,
        active_borrows=active_borrows,
        returned_borrows=returned_borrows,
        overdue_borrows=overdue_borrows,
        standard_members=standard_members,
        premium_members=premium_members,
        paid_fines=round(paid_fines, 2),
        unpaid_fines=round(unpaid_fines, 2),
        category_labels=category_labels,
        category_data=category_data,
        top_members=top_members,
        top_books=top_books
    )


# ==================== SEARCH & API ROUTES ====================

@main_bp.route('/search')
def search():
    """Global search across catalog and membership"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search.html', query='', books=[], members=[])
    
    # Search books
    books = Book.query.filter(
        or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.isbn.ilike(f'%{query}%'),
            Book.category.ilike(f'%{query}%'),
            Book.publisher.ilike(f'%{query}%')
        )
    ).limit(15).all()
    
    # Search members
    members = Member.query.filter(
        or_(
            Member.name.ilike(f'%{query}%'),
            Member.email.ilike(f'%{query}%'),
            Member.phone.ilike(f'%{query}%')
        )
    ).limit(15).all()
    
    return render_template(
        'search.html',
        query=query,
        books=books,
        members=members
    )


@main_bp.route('/api/books')
def api_books():
    """API endpoint for books (JSON)"""
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])


@main_bp.route('/api/members')
def api_members():
    """API endpoint for members (JSON)"""
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])


@main_bp.route('/api/borrows')
def api_borrows():
    """API endpoint for borrows (JSON)"""
    borrows = Borrow.query.all()
    return jsonify([borrow.to_dict() for borrow in borrows])


@main_bp.route('/api/stats')
def api_stats():
    """API endpoint for dynamic dashboard charts"""
    today = datetime.now()
    
    # Monthly borrow trends for the last 6 months
    months_labels = []
    months_counts = []
    for i in range(5, -1, -1):
        target_month_date = today - timedelta(days=i * 30)
        label = target_month_date.strftime('%b %Y')
        months_labels.append(label)
        # Approximate monthly count
        start_date = target_month_date.replace(day=1)
        # Next month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        count = Borrow.query.filter(Borrow.borrow_date >= start_date, Borrow.borrow_date < end_date).count()
        months_counts.append(count)
    
    # Status breakdown
    active_count = Borrow.query.filter(Borrow.status == 'active', Borrow.due_date >= today).count()
    overdue_count = Borrow.query.filter(Borrow.status == 'active', Borrow.due_date < today).count()
    returned_count = Borrow.query.filter_by(status='returned').count()
    
    # Categories
    category_counts = db.session.query(Book.category, func.count(Book.id)).group_by(Book.category).all()
    
    return jsonify({
        'trends': {
            'labels': months_labels,
            'data': months_counts
        },
        'status': {
            'labels': ['Active On-Time', 'Overdue', 'Returned'],
            'data': [active_count, overdue_count, returned_count]
        },
        'categories': {
            'labels': [c[0] or 'Other' for c in category_counts],
            'data': [c[1] for c in category_counts]
        }
    })