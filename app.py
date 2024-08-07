import streamlit as st
import sqlite3
from PIL import Image, ImageDraw, ImageFont
import os

# Use Bootstrap for styling
st.markdown(
    """
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
    """,
    unsafe_allow_html=True,
)

# Add custom CSS to fix background and text color issues
st.markdown(
    """
    <style>
    .card {
        background-color: #D9D9D9; /* Light background for cards */
        color: #212529; /* Dark text color for contrast */
    }
    .card-body {
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display product details
def display_product_info(product):
    internal_id, sku, description, old_sku, vendor, vendor_sku, vendor_description, on_hand_qty, type_, color_fullname, shape, size, packing_size = product[0:13]

    st.markdown(f"""
    <div class="card" style="margin: 20px 0;">
        <div class="card-body">
            <h5 class="card-title">{description}</h5>
            <table class="table" style="border-collapse: collapse; width: 100%;">
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Internal ID</th>
                    <td style="border: 2px solid darkgrey;">{internal_id}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">SKU</th>
                    <td style="border: 2px solid darkgrey;">{sku}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Old SKU</th>
                    <td style="border: 2px solid darkgrey;">{old_sku}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Vendor</th>
                    <td style="border: 2px solid darkgrey;">{vendor}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Vendor SKU</th>
                    <td style="border: 2px solid darkgrey;">{vendor_sku}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Vendor Description</th>
                    <td style="border: 2px solid darkgrey;">{vendor_description}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">On Hand Quantity</th>
                    <td style="border: 2px solid darkgrey;">{on_hand_qty}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Type</th>
                    <td style="border: 2px solid darkgrey;">{type_}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Color</th>
                    <td style="border: 2px solid darkgrey;">{color_fullname}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Shape</th>
                    <td style="border: 2px solid darkgrey;">{shape}</td>
                </tr>
                <tr style="border-bottom: 2px solid darkgrey;">
                    <th style="width: 30%; border: 2px solid darkgrey;">Size</th>
                    <td style="border: 2px solid darkgrey;">{size}mm</td>
                </tr>
                <tr>
                    <th style="width: 30%; border: 2px solid darkgrey;">Packing Size</th>
                    <td style="border: 2px solid darkgrey;">{packing_size}pcs</td>
                </tr>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('gem_info.db')
    return conn

# Fetch product data from the database
def get_product_data(conn):
    query = "SELECT internal_id, sku, description, old_sku, vendor, vendor_sku, vendor_description, on_hand_quantity, type, color_fullname, shape, size, packing_size FROM gems LEFT JOIN colors WHERE gems.'color' = colors.'color'"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

# Fetch shape-specific data
def get_shape_data(conn, shape, internal_id):
    if shape.lower() == 'round':
        query = f"""
        SELECT gems.internal_id, gems.shape, shape_round.diameter, shape_round.table_diameter, shape_round.crown_height, shape_round.pavilion_depth 
        FROM gems 
        LEFT JOIN shape_round ON gems.internal_id = shape_round.internal_id 
        WHERE gems.internal_id = '{internal_id}';
        """
    elif shape.lower() == 'marquise':
        query = f"""
        SELECT gems.internal_id, gems.shape, shape_marquise.length, shape_marquise.width, shape_marquise.depth 
        FROM gems 
        LEFT JOIN shape_marquise ON gems.internal_id = shape_marquise.internal_id 
        WHERE gems.internal_id = '{internal_id}';
        """
    else:
        return None
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

# Overlay text on the base image
def overlay_text_on_image(image_path, shape_data, shape, font_path='arial.ttf'):
    try:
        image = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, 18)  # Use the specified font

        if shape.lower() == 'round':
            diameter, table_diameter, crown_height, pavilion_depth = shape_data[2:6]
            draw.text((177, 20), f"Diameter: {diameter}mm", font=font, fill="black")
            draw.text((195, 53), f"Table: {table_diameter}mm", font=font, fill="black")
            draw.text((5, 100), f"Crown: {crown_height}mm", font=font, fill="black")
            draw.text((5, 193), f"Pavilion: {pavilion_depth}mm", font=font, fill="black")
        elif shape.lower() == 'marquise':
            length, width, depth = shape_data[2:5]
            draw.text((50, 50), f"Length: {length}mm", font=font, fill="black")
            draw.text((50, 80), f"Width: {width}mm", font=font, fill="black")
            draw.text((50, 110), f"Depth: {depth}mm", font=font, fill="black")

        return image

    except Exception as e:
        st.write(f"Error overlaying text: {e}")
        return None

# Display images
def display_images(internal_id, shape, conn):
    # Display packing photo
    packing_image_path = os.path.join("Packing", f"{internal_id}.png")
    if os.path.exists(packing_image_path):
        st.image(packing_image_path, caption="Packing Photo", use_column_width=True)
    else:
        st.write("No Packing Photo available.")

    # Display product photo
    product_image_path = os.path.join("Product", f"{internal_id}.png")
    if os.path.exists(product_image_path):
        st.image(product_image_path, caption="Product Photo", use_column_width=True)
    else:
        st.write("No Product Photo available.")

    # Display shape-specific image with dynamic measurements
    shape_image_path = os.path.join("shape", f"{shape.lower()}.jpg")
    # st.write(f"Checking for image at: {shape_image_path}")  # Debug message
    if os.path.exists(shape_image_path):
        shape_data = get_shape_data(conn, shape, internal_id)
        if shape_data:
            overlayed_image = overlay_text_on_image(shape_image_path, shape_data, shape)
            if overlayed_image:
                st.image(overlayed_image, caption=f"{shape.capitalize()} Shape Measurements", use_column_width=True)
            else:
                st.write("Error generating shape image.")
        else:
            st.write(f"No shape data available for {shape}.")
    else:
        st.write(f"No base image available for {shape} shape.")

# Filter products based on user input
# def filter_products(products, sku, type_, color, shape, size):
#     filtered = products
#     if sku:
#         filtered = [p for p in filtered if p[1].lower() == sku.lower()]
#     if type_:
#         filtered = [p for p in filtered if p[9].lower() == type_.lower()]
#     if color:
#         filtered = [p for p in filtered if p[10].lower() == color.lower()]
#     if shape:
#         filtered = [p for p in filtered if p[11].lower() == shape.lower()]
#     if size:
#         filtered = [p for p in filtered if p[12].lower() == size.lower()]
#     return filtered

# Main function
# Main function
def main():
    st.title("Gem Information Database")

    conn = get_db_connection()  # Open database connection
    product_data = get_product_data(conn)

    # User input for lookup
    st.sidebar.header("Search Product")
    sku = st.sidebar.text_input("Enter SKU (Leave empty if not applicable)")

    # Apply SKU filter if provided
    if sku:
        filtered_products = [p for p in product_data if str(p[1]) == sku]
    else:
        filtered_products = product_data

    # Available options for cascading filters based on filtered products
    types = sorted(set(str(p[8]) for p in filtered_products if p[8]))
    colors = sorted(set(str(p[9]) for p in filtered_products if p[9]))
    shapes = sorted(set(str(p[10]) for p in filtered_products if p[10]))
    sizes = sorted(set(str(p[11]) for p in filtered_products if p[11]))

    # Sidebar filters
    type_ = st.sidebar.selectbox("Select Type", [""] + types)
    color = st.sidebar.selectbox("Select Color", [""] + colors)
    shape = st.sidebar.selectbox("Select Shape", [""] + shapes)
    size = st.sidebar.selectbox("Select Size", [""] + sizes)

    # Apply remaining filters based on previous filter values
    if type_:
        filtered_products = [p for p in filtered_products if str(p[8]) == type_]
    if color:
        filtered_products = [p for p in filtered_products if str(p[9]) == color]
    if shape:
        filtered_products = [p for p in filtered_products if str(p[10]) == shape]
    if size:
        filtered_products = [p for p in filtered_products if str(p[11]) == size]

    if filtered_products:
        selected_product_id = st.selectbox("Select Product by SKU", [str(p[0]) for p in filtered_products])

        # Find and display the selected product's information
        for product in filtered_products:
            if str(product[0]) == selected_product_id:
                display_product_info(product)
                display_images(product[0], product[10], conn)  # Pass open connection here
                break
    else:
        st.write("No products found matching the criteria.")

    conn.close()  # Close database connection after operations

if __name__ == "__main__":
    main()