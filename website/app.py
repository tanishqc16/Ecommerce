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
