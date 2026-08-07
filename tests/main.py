import violit as vl
from sqlmodel import SQLModel, Session, create_engine, Field
from typing import Optional
from datetime import datetime

# PostgreSQL connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_violit"
engine = create_engine(DATABASE_URL)

# Define models
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

# Create tables
SQLModel.metadata.create_all(engine)

app = vl.App(title="Violit + PostgreSQL Test", theme="ocean")

def home_page():
    app.title("PostgreSQL Test")
    app.text("This app demonstrates Violit with PostgreSQL connection.")
    
    # Show item count
    with Session(engine) as session:
        from sqlmodel import select
        result = session.exec(select(Item))
        items = result.all()
        app.text(f"Total items: {len(items)}")
    
    # Add new item form
    app.markdown("### Add New Item")
    name = app.text_input("Item Name")
    description = app.text_input("Description (optional)")
    
    if app.button("Add Item"):
        if name.value:
            with Session(engine) as session:
                item = Item(name=name.value, description=description.value or None)
                session.add(item)
                session.commit()
                app.toast(f"Added item: {name.value}")
                # Clear inputs
                name.set("")
                description.set("")
    
    # List items
    app.markdown("### Items")
    with Session(engine) as session:
        from sqlmodel import select
        result = session.exec(select(Item))
        items = result.all()
        
        if not items:
            app.text("No items yet. Add one above!")
        else:
            for item in items:
                app.text(f"• {item.name} - {item.description or 'No description'}")

def settings_page():
    app.title("Settings")
    app.text("Database connection settings")
    
    # Show connection info
    app.markdown("### Connection Info")
    app.text(f"Database: test_violit")
    app.text(f"Host: localhost")
    app.text(f"Port: 5432")
    app.text(f"User: postgres")

# Setup sidebar and navigation
with app.sidebar:
    app.markdown("## Navigation")

app.navigation([
    vl.Page(home_page, title="Home", icon="house"),
    vl.Page(settings_page, title="Settings", icon="gear"),
])

if __name__ == "__main__":
    app.run()
