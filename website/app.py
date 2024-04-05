# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)

# # Sample data for products and cart
# products = [
#     {"id": 1, "name": "Product 1", "price": 10, "description": "Description 1"},
#     {"id": 2, "name": "Product 2", "price": 20, "description": "Description 2"},
#     {"id": 3, "name": "Product 3", "price": 30, "description": "Description 3"},
# ]

# cart = {}

# @app.route('/')
# def index():
#     return render_template('index.html', products=products)

# @app.route('/all_products')
# def all_products():
#     return jsonify({"products": products})

# @app.route('/add_product', methods=['POST'])
# def add_product():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'Invalid JSON data'}), 400

#     new_product = {
#         'id': len(products) + 1,
#         'name': data.get('name'),
#         'price': data.get('price'),
#         'description': data.get('description')
#     }
#     products.append(new_product)
#     return jsonify(new_product), 201

# # Search route to search for products based on a keyword
# @app.route('/search_products', methods=['GET'])
# def search_products():
#     keyword = request.args.get('keyword')
#     if not keyword:
#         return jsonify({'error': 'Please provide a keyword to search for'}), 400

#     # Search for products containing the keyword in their name or description
#     matching_products = []
#     for product in products:
#         if keyword.lower() in product['name'].lower() or keyword.lower() in product['description'].lower():
#             matching_products.append(product)

#     if not matching_products:
#         return jsonify({'message': 'No products found matching the keyword'}), 404

#     return jsonify(matching_products)


# @app.route('/cart', methods=['GET'])
# def view_cart():
    
#     user_id = request.args.get('user_id')
#     user_cart = cart.get(user_id, {})
#     cart_items = []

#     for product_id, quantity in user_cart.items():
#         product = next((p for p in products if p['id'] == product_id), None)
#         if product:
#             item_total = product['price'] * quantity
#             cart_items.append({
#                 'product_id': product_id,
#                 'name': product['name'],
#                 'price': product['price'],
#                 'quantity': quantity,
#                 'item_total': item_total
#             })

#     total_amount = sum(item['item_total'] for item in cart_items)
#     return jsonify({
#         'cart_items': cart_items,
#         'total_amount': total_amount
#     })

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     product_id = data.get('product_id')
#     quantity = data.get('quantity', 1)

#     product = next((p for p in products if p['id'] == product_id), None)
#     if not product:
#         return jsonify({'error': 'Product not found'}), 404

#     user_cart = cart.get(user_id, {})
#     user_cart[product_id] = user_cart.get(product_id, 0) + quantity
#     cart[user_id] = user_cart

#     return jsonify(cart[user_id])

# @app.route('/delete_from_cart', methods=['POST'])
# def delete_from_cart():
#     data = request.get_json()
#     user_id = data.get('user_id')
#     product_id = data.get('product_id')

#     user_cart = cart.get(user_id, {})
#     if product_id in user_cart:
#         del user_cart[product_id]
#         cart[user_id] = user_cart

#     return jsonify(cart[user_id])

# if __name__ == '__main__':
#     app.run(debug=True)




# from flask import Flask, render_template, request, jsonify, redirect, url_for
# from pymongo import MongoClient
# from bson import ObjectId
# app = Flask(__name__)

# client = MongoClient("mongodb+srv://tanishqbc16:mongo123@cluster0.69f3cxq.mongodb.net/ecommerce?retryWrites=true&w=majority") 

# # db = client["ecommmerce"]
# # user_c = db["user"]

# # document = {"name":"tanishq"}
# # inserted_document = user_c.insert_one(document)
# # print({inserted_document.inserted_id})
# @app.route('/contact', methods=['GET'])
# def contact():
#     user_id = request.args.get('user_id')
#     return render_template("contact.html", user_id=user_id)

# if __name__ == '__main__':
#     app.run(debug=True)

    

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb+srv://tanishqbc16:njBnlrzn28PjI9pR@cluster0.69f3cxq.mongodb.net/ecommerce?retryWrites=true&w=majority&appName=Cluster0") 
db = client["ecommerce"]
products_collection = db["products"]
carts_collection = db["carts"]
user_collection = db["users"]

@app.route('/')
def index():
    # Get the user_id from the query parameters
    user_id = request.args.get('user_id')
    
    # Fetch products from the database
    products = list(products_collection.find())
    
    # Render the index.html template with products and user_id
    return render_template('index.html', products = products, user_id = user_id)

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    result = products_collection.insert_one(data)
    new_product = products_collection.find_one({"_id": result.inserted_id}, {"_id": 0})
    return jsonify(new_product), 201

@app.route('/search_products', methods=['GET'])
def search_products():
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({'error': 'Please provide a keyword to search for'}), 400

    matching_products = list(products_collection.find({
        "$or": [
            {"name": {"$regex": keyword, "$options": "i"}},
            {"description": {"$regex": keyword, "$options": "i"}}
        ]
    }, {"_id": 0}))

    if not matching_products:
        return jsonify({'message': 'No products found matching the keyword'}), 404

    print(matching_products)  # Log the matching products
    return jsonify(matching_products)

@app.route('/cart', methods=['GET'])
def get_cart_products():
    try:
        user_id = request.args.get('user_id')
        user_id = ObjectId(user_id)
        
        # Query the database to get all cart documents for the user
        cart_products_cursor = carts_collection.find({"user_id": user_id})
        
        # Count the number of documents
        cart_products_count = sum(1 for _ in cart_products_cursor)
        
        # Reset cursor to the beginning
        cart_products_cursor.rewind()
        
        if cart_products_count == 0:
            return jsonify({"error": "Cart not found for the user."}), 404

        # Initialize a list to store products
        products = []

        # Iterate through each cart document
        for cart_doc in cart_products_cursor:
            # Fetch product details for each product in the cart
            for product_id in cart_doc.get("products", []):
                product = products_collection.find_one({"_id": product_id})
                if product:
                    # Convert ObjectId to string for JSON serialization
                    product['_id'] = str(product['_id'])
                    products.append(product)
        return jsonify({"products": products}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/carts', methods=['GET'])
def view_cart():
    user_id = request.args.get('user_id')
    return render_template('cart.html', user_id=user_id)





@app.route("/signin", methods=['GET'])
def signin():
    return render_template("login.html")


@app.route("/admin/addProduct", methods=['GET'])
def addProduct():
    return render_template("AddProduct.html")


@app.route('/products', methods=['GET'])
def display_products():
    user_id = request.args.get('user_id')
    products = list(products_collection.find({}, {"_id": 0}))
    return render_template('product.html', products=products, user_id=user_id)

@app.route("/signup", methods=["GET"])
def signup():
    return render_template("signup.html")

from flask import jsonify

@app.route('/register', methods=['POST'])
def register():
    # Get form data
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')

    # Check if username or email already exists in the database
    existing_user = user_collection.find_one({"$or": [{"username": username}, {"email": email}]})
    if existing_user:
        return jsonify({'error': 'Username or email already exists'}), 400

    # Insert new user into the database
    new_user = {
        "username": username,
        "email": email,
        "phone": phone,
        "password": password  # Store password as plain text (not recommended)
    }
    user_collection.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    # Retrieve email and password from the request
    email = request.json.get('email')
    password = request.json.get('password')

    # Find the user in the database
    user = user_collection.find_one({"email": email})

    # Check if the user exists and if the password matches
    if user and user['password'] == password:
        # Fetch the user ID
        user_id = str(user['_id'])
        return jsonify({'user_id': user_id})  # Return user_id to the client
    else:
        return jsonify({'error': 'Invalid email or password'}), 401



@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
        data = request.json
        
        # Extract data from the request
        user_id = ObjectId(data.get('user_id'))
        product_id = ObjectId(data.get('product_id'))
        
        # Validate user_id and product_id
        if not user_id or not product_id:
            raise ValueError("User ID or Product ID is missing.")

        # Check if the product exists in the products collection
        product = products_collection.find_one({"_id": product_id})
        if not product:
            raise ValueError("Product not found.")

        # Check if the user exists in the user collection
        user = user_collection.find_one({"_id": user_id})
        if not user:
            raise ValueError("User not found.")

        # Check if the user has an existing cart
        existing_cart = carts_collection.find_one({"user_id": user_id})

        if existing_cart:
            # Check if the product is already in the cart
            if product_id in existing_cart['products']:
                return jsonify({"message": "Product already exists in the cart.", "cart_id": str(existing_cart["_id"])}), 200

            # Update the existing cart with the new product
            carts_collection.update_one({"_id": existing_cart["_id"]}, {"$push": {"products": product_id}})
            return jsonify({"message": "Product added to cart successfully.", "cart_id": str(existing_cart["_id"])}), 200
        else:
            # Create a new cart for the user with the current product
            cart_id = ObjectId()  # Generate a unique cart ID
            carts_collection.insert_one({"_id": cart_id, "user_id": user_id, "products": [product_id]})
            return jsonify({"message": "Product added to cart successfully.", "cart_id": str(cart_id)}), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400   
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400





# @app.route('/checkout', methods=['POST'])
# def checkout():
#     try:
#         # Extract user_id and products from the request
#         user_id = request.json.get('user_id')
#         products = request.json.get('products')

#         # Validate user_id
#         if not user_id:
#             raise ValueError("User ID is missing.")

#         # Validate products
#         if not products:
#             raise ValueError("No products in the cart.")

#         # Convert product IDs to ObjectId
#         product_ids = [ObjectId(pid) for pid in products]

#         # Fetch product details from the database
#         product_details = []
#         for product_id in product_ids:
#             product = products_collection.find_one({"_id": product_id})
#             if product:
#                 product_details.append(product)
#             else:
#                 raise ValueError(f"Product not found: {product_id}")

#         # Store transaction in the transaction collection
#         transaction = {
#             "user_id": ObjectId(user_id),
#             "products": product_details
#         }
#         transaction_id = transaction_collection.insert_one(transaction).inserted_id

#         # Delete all products from the user's cart
#         carts_collection.delete_many({"user_id": ObjectId(user_id)})

#         # Display success message
#         return jsonify({"message": f"Transaction completed successfully. Transaction ID: {transaction_id}"}), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

# from bson import ObjectId  # Import ObjectId from bson module

# @app.route('/transactions', methods=['GET'])
# def get_transactions():
#     print(request)
#     try:
#         # Get the user_id from the query parameters
#         user_id = request.args.get('user_id')
#         user_id = ObjectId(user_id)
#         print(user_id)
        
#         # Query the database to get all transactions for the user
#         user_transactions = list(transaction_collection.find({"user_id": user_id}))
        
#         # If no transactions found, return an error
#         if not user_transactions:
#             return jsonify({"error": "No transactions found for the user."}), 404

#         # Initialize a list to store formatted transaction details
#         formatted_transactions = []

#         # Iterate through each transaction document
#         for transaction in user_transactions:
#             # Convert ObjectId to string for _id
#             transaction["_id"] = str(transaction["_id"])

#             # Format product details
#             products = []
#             for product in transaction["products"]:
#                 print(product)
#                 product_info = {
#                     "_id": str(product["_id"]),  # Using _id instead of id
#                     "name": product['name'],
#                     "price": product['price'],
#                     "description": product['description']
#                 }
#                 products.append(product_info)


#             # Create a formatted transaction object
#             formatted_transaction = {
#                 "_id": transaction["_id"],
#                 "user_id": str(transaction["user_id"]),
#                 "products": products
#             }
#             formatted_transactions.append(formatted_transaction)
#         return jsonify({"transactions": formatted_transactions}), 200

#     except Exception as e:
#         print("Error:", e)
#         return jsonify({"error": str(e)}), 500

# @app.route('/transaction', methods=['GET'])
# def view_transactions():
#     try:
#         # Get the user_id from the query parameters
#         user_id = request.args.get('user_id')
        
#         # Render the transactions.html template with the user_id
#         return render_template('transaction.html', user_id=user_id)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 400


@app.route('/aboutus', methods=['GET'])
def aboutus():
    user_id = request.args.get('user_id')
    return render_template("aboutus.html", user_id=user_id)


@app.route('/home', methods=['GET'])
def contact():
    user_id = request.args.get('user_id')
    return render_template("home.html", user_id=user_id)

@app.route('/profile', methods=['GET'])
def profile():
    user_id = request.args.get('user_id')
    return render_template("profile.html", user_id=user_id)

@app.route('/user_info', methods=['GET'])
def get_user_info():
    try:
        # Get the user_id from the query parameters
        user_id = request.args.get('user_id')
        user_id = ObjectId(user_id)
        # print("user id",user_id)
        
        # Query the database to get the user information
        user_info = user_collection.find_one({"_id": user_id})
        
        # If user not found, return an error
        if not user_info:
            return jsonify({"error": "User not found."}), 404

        # Convert ObjectId to string
        user_info["_id"] = str(user_info["_id"])
        # print(user_info)
        return jsonify({"user_info": user_info}), 200

    except Exception as e:
        print("Error", e)
        return jsonify({"error": str(e)}), 500

@app.route('/delete_from_cart', methods=['DELETE'])
def delete_from_cart():
    try:
        # Extract user ID and product ID from the request
        user_id = ObjectId(request.args.get('user_id'))
        product_id = ObjectId(request.args.get('product_id'))

        # Validate user ID and product ID
        if not user_id or not product_id:
            raise ValueError("User ID or Product ID is missing.")

        # Remove the product from the user's cart
        carts_collection.update_one({"user_id": user_id}, {"$pull": {"products": product_id}})

        return jsonify({"message": "Product deleted from cart successfully."}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
