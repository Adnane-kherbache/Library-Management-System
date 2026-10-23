import os
import sys
from app import create_app, db
from app.models import Book, Member, Borrow

# Ensure safe stdout encoding on Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """
    Make database models available in Flask shell
    Usage: flask shell
    """
    return {
        'db': db,
        'Book': Book,
        'Member': Member,
        'Borrow': Borrow
    }


@app.cli.command()
def init_db():
    """
    Initialize the database with tables
    Usage: flask init-db
    """
    db.create_all()
    print('[OK] Database initialized successfully!')


@app.cli.command()
def seed_db():
    """
    Seed the database with comprehensive sample data
    Usage: flask seed-db
    """
    from datetime import datetime, timedelta
    
    print('[*] Clearing existing data...')
    Borrow.query.delete()
    Book.query.delete()
    Member.query.delete()
    db.session.commit()
    
    print('[*] Adding curated library books...')
    books = [
        Book(
            title='The Great Gatsby',
            author='F. Scott Fitzgerald',
            isbn='9780743273565',
            category='Fiction',
            publication_year=1925,
            publisher='Scribner',
            description='A classic American novel exploring the decadence and idealism of the Roaring Twenties in New York.',
            quantity=4,
            available=4
        ),
        Book(
            title='To Kill a Mockingbird',
            author='Harper Lee',
            isbn='9780061120084',
            category='Fiction',
            publication_year=1960,
            publisher='J.B. Lippincott & Co.',
            description='A timeless story of racial injustice, moral courage, and childhood innocence in Maycomb, Alabama.',
            quantity=3,
            available=3
        ),
        Book(
            title='1984',
            author='George Orwell',
            isbn='9780451524935',
            category='Science Fiction',
            publication_year=1949,
            publisher='Secker & Warburg',
            description='The quintessential dystopian masterpiece chronicling omnipresent surveillance, truth manipulation, and thoughtcrime.',
            quantity=5,
            available=5
        ),
        Book(
            title='Dune',
            author='Frank Herbert',
            isbn='9780441013593',
            category='Science Fiction',
            publication_year=1965,
            publisher='Chilton Books',
            description='An epic science-fiction chronicle of politics, religion, ecology, and technology on the desert planet Arrakis.',
            quantity=4,
            available=4
        ),
        Book(
            title='Clean Code: A Handbook of Agile Software Craftsmanship',
            author='Robert C. Martin',
            isbn='9780132350884',
            category='Technology',
            publication_year=2008,
            publisher='Prentice Hall',
            description='Essential principles, patterns, and practices for writing readable, maintainable, and elegant software code.',
            quantity=3,
            available=3
        ),
        Book(
            title='The Pragmatic Programmer',
            author='David Thomas, Andrew Hunt',
            isbn='9780135957059',
            category='Technology',
            publication_year=2019,
            publisher='Addison-Wesley',
            description='Timeless lessons on software craft, engineering discipline, career mastery, and architectural thinking.',
            quantity=4,
            available=4
        ),
        Book(
            title='Harry Potter and the Philosopher\'s Stone',
            author='J.K. Rowling',
            isbn='9780747532699',
            category='Fantasy',
            publication_year=1997,
            publisher='Bloomsbury',
            description='The opening chapter of the beloved wizarding saga at Hogwarts School of Witchcraft and Wizardry.',
            quantity=5,
            available=5
        ),
        Book(
            title='The Hobbit',
            author='J.R.R. Tolkien',
            isbn='9780547928227',
            category='Fantasy',
            publication_year=1937,
            publisher='George Allen & Unwin',
            description='Bilbo Baggins embarks on a dangerous adventure across Middle-earth to reclaim the Lonely Mountain and its treasure.',
            quantity=3,
            available=3
        ),
        Book(
            title='Sapiens: A Brief History of Humankind',
            author='Yuval Noah Harari',
            isbn='9780062316097',
            category='History',
            publication_year=2014,
            publisher='Harper',
            description='A groundbreaking survey of the evolutionary, cognitive, agricultural, and scientific revolutions of humankind.',
            quantity=3,
            available=3
        ),
        Book(
            title='Steve Jobs',
            author='Walter Isaacson',
            isbn='9781451648539',
            category='Biography',
            publication_year=2011,
            publisher='Simon & Schuster',
            description='The definitive, intimate biography of the visionary Apple co-founder who revolutionized multiple global industries.',
            quantity=2,
            available=2
        ),
        Book(
            title='The Da Vinci Code',
            author='Dan Brown',
            isbn='9780307474278',
            category='Thriller',
            publication_year=2003,
            publisher='Doubleday',
            description='Symbologist Robert Langdon unravels a clandestine conspiracy woven into classic Renaissance art and history.',
            quantity=3,
            available=3
        ),
        Book(
            title='Meditations',
            author='Marcus Aurelius',
            isbn='9780140449334',
            category='Philosophy',
            publication_year=180,
            publisher='Penguin Classics',
            description='Personal reflections and Stoic wisdom from the Roman Emperor on resilience, mindfulness, duty, and life.',
            quantity=3,
            available=3
        )
    ]
    
    for book in books:
        db.session.add(book)
    db.session.commit()
    
    print('[*] Adding library members...')
    members = [
        Member(
            name='Sofia Alami',
            email='sofia.alami@example.com',
            phone='+212 612-345678',
            address='124 Boulevard d\'Anfa, Casablanca',
            membership_type='premium'
        ),
        Member(
            name='Youssef Benali',
            email='youssef.benali@example.com',
            phone='+212 623-456789',
            address='45 Avenue Mohammed V, Rabat',
            membership_type='standard'
        ),
        Member(
            name='Fatima Ezzahra',
            email='fatima.ezzahra@example.com',
            phone='+212 634-567890',
            address='78 Rue de la Liberté, Marrakech',
            membership_type='premium'
        ),
        Member(
            name='Karim Mansouri',
            email='karim.mansouri@example.com',
            phone='+212 645-678901',
            address='12 Rue Ibn Battouta, Tangier',
            membership_type='standard'
        ),
        Member(
            name='Nour El Houda',
            email='nour.elhouda@example.com',
            phone='+212 656-789012',
            address='33 Avenue Hassan II, Agadir',
            membership_type='standard'
        ),
        Member(
            name='Omar Tazi',
            email='omar.tazi@example.com',
            phone='+212 667-890123',
            address='89 Boulevard Zerktouni, Fes',
            membership_type='premium'
        )
    ]
    
    for member in members:
        db.session.add(member)
    db.session.commit()
    
    print('[*] Creating borrow records (active, overdue, and returned)...')
    now = datetime.now()
    
    borrows = [
        # Active borrow (in good standing)
        Borrow(
            book_id=books[0].id,
            member_id=members[0].id,
            borrow_date=now - timedelta(days=6),
            due_date=now + timedelta(days=8),
            status='active'
        ),
        # Active borrow (close to due)
        Borrow(
            book_id=books[2].id,
            member_id=members[1].id,
            borrow_date=now - timedelta(days=12),
            due_date=now + timedelta(days=2),
            status='active'
        ),
        # Active borrow that is OVERDUE (5 days late, pending fine)
        Borrow(
            book_id=books[4].id,
            member_id=members[2].id,
            borrow_date=now - timedelta(days=25),
            due_date=now - timedelta(days=5),
            status='active'
        ),
        # Returned on time ($0 fine)
        Borrow(
            book_id=books[1].id,
            member_id=members[3].id,
            borrow_date=now - timedelta(days=40),
            due_date=now - timedelta(days=26),
            return_date=now - timedelta(days=28),
            status='returned',
            fine_amount=0.0,
            fine_paid=True
        ),
        # Returned late, fine paid ($8.00)
        Borrow(
            book_id=books[6].id,
            member_id=members[0].id,
            borrow_date=now - timedelta(days=50),
            due_date=now - timedelta(days=36),
            return_date=now - timedelta(days=28),
            status='returned',
            fine_amount=8.0,
            fine_paid=True
        ),
        # Returned late, fine UNPAID ($12.00)
        Borrow(
            book_id=books[7].id,
            member_id=members[4].id,
            borrow_date=now - timedelta(days=60),
            due_date=now - timedelta(days=46),
            return_date=now - timedelta(days=34),
            status='returned',
            fine_amount=12.0,
            fine_paid=False
        ),
        # Additional historical borrow for popularity
        Borrow(
            book_id=books[0].id,
            member_id=members[5].id,
            borrow_date=now - timedelta(days=90),
            due_date=now - timedelta(days=76),
            return_date=now - timedelta(days=78),
            status='returned',
            fine_amount=0.0,
            fine_paid=True
        ),
        Borrow(
            book_id=books[2].id,
            member_id=members[5].id,
            borrow_date=now - timedelta(days=70),
            due_date=now - timedelta(days=56),
            return_date=now - timedelta(days=55),
            status='returned',
            fine_amount=0.0,
            fine_paid=True
        )
    ]
    
    for borrow in borrows:
        db.session.add(borrow)
        if borrow.status == 'active':
            # Deduct availability
            borrow_book_obj = Book.query.get(borrow.book_id)
            if borrow_book_obj:
                borrow_book_obj.borrow_book()
    
    db.session.commit()
    
    print('[OK] Database seeded successfully!')
    print(f'     Books: {Book.query.count()}')
    print(f'     Members: {Member.query.count()}')
    print(f'     Borrows: {Borrow.query.count()}')


@app.cli.command()
def drop_db():
    """
    Drop all database tables
    Usage: flask drop-db
    """
    if input('Are you sure you want to drop all tables? (yes/no): ').lower() == 'yes':
        db.drop_all()
        print('[OK] Database tables dropped successfully!')
    else:
        print('[!] Operation cancelled.')


@app.cli.command()
def reset_db():
    """
    Reset database (drop, create, seed)
    Usage: flask reset-db
    """
    print('[*] Resetting database...')
    db.drop_all()
    db.create_all()
    
    from flask.cli import with_appcontext
    ctx = app.app_context()
    ctx.push()
    seed_db.callback()
    ctx.pop()
    print('[OK] Database reset complete!')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )