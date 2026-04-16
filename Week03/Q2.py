cart = ["apple", "banana", "milk", "apple", "bread", "eggs"]
apple_count = cart.count("apple")
print(f"Number of apples in the cart : {apple_count}")
milk_position = cart.index("milk")
print(f"position of milk in the cart : {milk_position}")
cart.remove("eggs") #using remove
removed_item = cart.pop()

print(f"Removed item using pop : {removed_item}")
print(" Is banana is in my cart ?", "banana" in cart )
