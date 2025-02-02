# Portfolio Manager Backend

[GitHub Repository](https://github.com/officialasishkumar/portfolio-manager-backend)

The **Portfolio Manager Backend** is a mock exchange backend built using [FastAPI](https://fastapi.tiangolo.com/). It provides RESTful endpoints for user authentication, order management (placing, amending, executing, and canceling orders), and portfolio overview. The backend leverages SQLAlchemy for ORM functionality, passlib for password hashing, and OAuth2 for authentication.

---

## Features

- **User Authentication:**  
  - Login endpoint that authenticates users using OAuth2 password flow.
  - Secure password hashing using bcrypt.
  - Token-based authentication for subsequent API requests.

- **User Management:**  
  - Create new users (for testing/demo purposes).

- **Order Management:**  
  - Place new orders with details such as security and quantity.
  - Amend orders (with validation to ensure the new quantity is valid).
  - Execute orders by specifying the executed quantity.
  - Cancel orders that are pending or partially executed.
  - List all orders for an authenticated user.

- **Portfolio Overview:**  
  - Retrieve the current portfolio by aggregating executed order quantities by security.

---

## Directory Structure

```plaintext
.
├── auth.py
├── crud.py
├── database.py
├── main.py
├── models.py
└── schemas.py
```

- **auth.py:**  
  Contains utilities for authentication including password hashing and token validation.

- **crud.py:**  
  Implements CRUD operations for users, orders, and tokens using SQLAlchemy.

- **database.py:**  
  Sets up the database connection and ORM base using SQLAlchemy. Supports SQLite by default with optional PostgreSQL configuration.

- **main.py:**  
  The main FastAPI application that defines all REST endpoints for authentication and order operations.

- **models.py:**  
  SQLAlchemy models for users, orders, and tokens. Defines relationships and order status enums.

- **schemas.py:**  
  Pydantic models for request validation and response serialization.

---

## Getting Started

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [virtualenv](https://virtualenv.pypa.io/en/latest/) for creating an isolated environment

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/officialasishkumar/portfolio-manager-backend.git
   cd portfolio-manager-backend
   ```

2. **Create and activate a virtual environment (recommended):**

   ```bash
   python -m venv venv
   # On Unix or MacOS:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** If a `requirements.txt` file is not provided, you can install the required packages manually:
   >
   > ```bash
   > pip install fastapi uvicorn sqlalchemy python-dotenv passlib[bcrypt] pydantic
   > ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root to set your database URL. For example, to use SQLite (default):

   ```env
   DATABASE_URL=sqlite:///./exchange.db
   ```

   If using PostgreSQL:

   ```env
   DATABASE_URL=postgresql://username:password@localhost/dbname
   ```

5. **Initialize the Database:**

   The database tables will be automatically created when you start the FastAPI application (via the call to `models.Base.metadata.create_all(bind=engine)` in `main.py`).

### Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

- The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
- You can view the interactive API documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## API Endpoints

### Authentication

- **POST `/login`**  
  Authenticate a user and receive an access token.  
  _Request_: `username`, `password`  
  _Response_: Access token and token type.

- **POST `/users`**  
  Create a new user (for testing/demo purposes).  
  _Request_: `username`, `password`  
  _Response_: Created user's username and a hidden password message.

### Orders

- **POST `/orders`**  
  Place a new order.  
  _Request_: `security`, `qty`  
  _Response_: Order details including status and pending quantity.

- **PUT `/orders/{order_id}`**  
  Amend an existing order's quantity.  
  _Request_: New quantity (`qty`)  
  _Response_: Updated order details.

- **DELETE `/orders/{order_id}`**  
  Cancel an order.  
  _Response_: Order details with status updated to `cancelled`.

- **GET `/orders`**  
  List all orders for the authenticated user.  
  _Response_: A list of order details.

- **POST `/orders/{order_id}/execute`**  
  Execute an order by specifying an executed quantity.  
  _Request_: `executed_qty`  
  _Response_: Updated order details with new executed quantity and status.

### Portfolio

- **GET `/portfolio`**  
  Get a summary of executed orders by security.  
  _Response_: List of portfolio items showing each security and total executed quantity.

---

## Contributing

Contributions are welcome! If you'd like to improve the project, feel free to fork the repository and submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For any questions or suggestions, please open an issue in the [GitHub repository](https://github.com/officialasishkumar/portfolio-manager-backend) or contact the repository owner.

Happy coding!