import streamlit as st
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, db
import time

# Only initialize Firebase once
if not firebase_admin._apps:
    # Write secrets to a temporary JSON file (for Firebase Admin SDK)
    firebase_json_path = "/tmp/firebase_key.json"
    with open(firebase_json_path, "w") as f:
        json.dump(st.secrets["firebase"], f)

    # Initialize Firebase app
    cred = credentials.Certificate(firebase_json_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://bush-bar-coffee-order-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# --- Routing ---
page = st.sidebar.selectbox("Choose View", ["Member Order Form", "Staff Dashboard"])

# --- Member View ---
if page == "Member Order Form":
    st.title("⛳️ Halfway House Coffee Order")

    member_id = st.text_input("Member Number")
    coffee = st.selectbox("☕ Select Coffee", ["Latte", "Flat White", "Long Black", "Cappuccino", "Espresso"])
    size = st.radio("📏 Size", ["Regular", "Large"], horizontal=True)
    milk = st.selectbox("🥛 Milk Type", ["Full Cream", "Skim", "Almond", "Soy", "Oat"])
    notes = st.text_input("📝 Notes (optional)")
    if st.button("Place Order"):
        if not member_id:
            st.error("Please enter your member number.")
        else:
            ref = db.reference("orders")
            ref.push({
                "member_id": member_id,
                "coffee": coffee,
                "size": size,
                "milk": milk,
                "notes": notes,
                "status": "pending",
                "timestamp": int(time.time())
            })
            st.success("✅ Order placed! It’ll be ready at the halfway house.")

# --- Staff View ---
elif page == "Staff Dashboard":
    st.title("☕ Staff Order Dashboard")
    st_autorefresh(interval=20000, limit=None, key="staff_refresh")

    # Simple password protection
    if "authenticated" not in st.session_state:
        password = st.text_input("Enter staff password", type="password")
        if password == "bushbar2025":  # 🔒 Change this to a more secure one later
            st.session_state.authenticated = True
        else:
            st.stop()

    st.success("Access granted ✅")

    orders_ref = db.reference("orders")
    orders = orders_ref.get()

    if not orders:
        st.info("No current orders.")
    else:
        for order_id, order in orders.items():
            with st.expander(f"Order from Member {order.get('member_id')}"):
                st.write(f"**Coffee:** {order.get('coffee')}")
                st.write(f"**Size:** {order.get('size')}")
                st.write(f"**Milk:** {order.get('milk')}")
                st.write(f"**Notes:** {order.get('notes')}")
                st.write(f"**Time:** {time.strftime('%H:%M:%S', time.localtime(order.get('timestamp')))}")
                if st.button("✅ Mark Order as Completed", key=order_id):
                    orders_ref.child(order_id).delete()
                    st.success("Order marked as completed.")
                    st.rerun()
