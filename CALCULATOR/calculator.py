def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Division by zero is not allowed."
    return a / b

while True:
    print("\n=== WELCOME TO MY CLI CALCULATOR  ===")
    print("1. Addition (+)")  
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Quit")

    choice = input("Choose an option: ").strip()

    if choice == "5":
        print("Goodbye!")
        break

    if choice not in ("1", "2", "3", "4"):
        print("Invalid choice! Enter a number from 1 to 5.")
        continue

    while True:
        try:
            num1 = float(input("Enter first number: "))
            num2 = float(input("Enter second number: "))
            break
        except ValueError:
            print("Invalid input! Please enter numbers only.")

    if choice == "1":
        result = add(num1, num2)
    elif choice == "2":
        result = subtract(num1, num2)
    elif choice == "3":
        result = multiply(num1, num2)
    else:
        result = divide(num1, num2)

    print("Result:", result)